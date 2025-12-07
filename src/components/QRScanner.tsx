import { useState, useRef, useEffect } from 'react';
import jsQR from 'jsqr';
import { Camera, X, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface QRScannerProps {
    onScan: (data: string) => void;
    onClose?: () => void;
}

export const QRScanner = ({ onScan, onClose }: QRScannerProps) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [isScanning, setIsScanning] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const requestRef = useRef<number>();

    useEffect(() => {
        let stream: MediaStream | null = null;

        const startCamera = async () => {
            try {
                stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: 'environment' }
                });

                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                    // Wait for video to be ready
                    videoRef.current.setAttribute('playsinline', 'true');
                    videoRef.current.play();
                    requestRef.current = requestAnimationFrame(tick);
                }
            } catch (err) {
                console.error("Error accessing camera:", err);
                setError("Could not access camera. Please ensure you have granted permission.");
                setIsScanning(false);
            }
        };

        if (isScanning) {
            startCamera();
        }

        return () => {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            if (requestRef.current) {
                cancelAnimationFrame(requestRef.current);
            }
        };
    }, [isScanning]);

    const tick = () => {
        if (videoRef.current && videoRef.current.readyState === videoRef.current.HAVE_ENOUGH_DATA) {
            const canvas = canvasRef.current;
            if (canvas) {
                canvas.height = videoRef.current.videoHeight;
                canvas.width = videoRef.current.videoWidth;
                const ctx = canvas.getContext('2d');

                if (ctx) {
                    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

                    const code = jsQR(imageData.data, imageData.width, imageData.height, {
                        inversionAttempts: "dontInvert",
                    });

                    if (code) {
                        // Found a QR code
                        onScan(code.data);
                        setIsScanning(false); // Stop scanning
                        return; // Stop loop
                    }
                }
            }
        }
        requestRef.current = requestAnimationFrame(tick);
    };

    const handleRetry = () => {
        setError(null);
        setIsScanning(true);
    };

    return (
        <div className="relative overflow-hidden rounded-xl bg-black aspect-video flex items-center justify-center border border-white/10 shadow-2xl">
            {error ? (
                <div className="text-center p-6">
                    <p className="text-destructive mb-4">{error}</p>
                    <button
                        onClick={handleRetry}
                        className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors mx-auto text-sm"
                    >
                        <RefreshCw className="h-4 w-4" />
                        Retry Camera
                    </button>
                </div>
            ) : (
                <>
                    <video
                        ref={videoRef}
                        className="absolute inset-0 w-full h-full object-cover"
                    />
                    <canvas ref={canvasRef} className="hidden" />

                    {/* Scanning Overlay */}
                    <div className="absolute inset-0 pointer-events-none">
                        <div className="absolute inset-0 border-[40px] border-black/50">
                            <div className="relative h-full w-full border-2 border-primary/50">
                                {/* Corner Markers */}
                                <div className="absolute top-0 left-0 w-8 h-8 border-t-4 border-l-4 border-primary"></div>
                                <div className="absolute top-0 right-0 w-8 h-8 border-t-4 border-r-4 border-primary"></div>
                                <div className="absolute bottom-0 left-0 w-8 h-8 border-b-4 border-l-4 border-primary"></div>
                                <div className="absolute bottom-0 right-0 w-8 h-8 border-b-4 border-r-4 border-primary"></div>

                                {/* Scanning Line */}
                                <motion.div
                                    className="absolute left-0 right-0 h-0.5 bg-primary shadow-[0_0_10px_rgba(var(--primary),0.8)]"
                                    animate={{ top: ['0%', '100%', '0%'] }}
                                    transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                                />
                            </div>
                        </div>
                        <div className="absolute bottom-4 left-0 right-0 text-center">
                            <p className="text-white/80 text-sm font-medium bg-black/50 inline-block px-3 py-1 rounded-full backdrop-blur-sm">
                                Align QR code within frame
                            </p>
                        </div>
                    </div>

                    {onClose && (
                        <button
                            onClick={onClose}
                            className="absolute top-2 right-2 p-2 bg-black/50 hover:bg-black/70 rounded-full text-white transition-colors z-10"
                        >
                            <X className="h-5 w-5" />
                        </button>
                    )}
                </>
            )}
        </div>
    );
};
