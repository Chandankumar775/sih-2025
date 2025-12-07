import { useState, useRef, useEffect } from 'react';
import { Mic, MicOff } from 'lucide-react';
import { motion } from 'framer-motion';

interface VoiceRecorderProps {
    onTranscript: (text: string) => void;
    language?: string;
}

export const VoiceRecorder = ({ onTranscript, language = 'en-US' }: VoiceRecorderProps) => {
    const [isRecording, setIsRecording] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [isSupported, setIsSupported] = useState(true);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const recognitionRef = useRef<any>(null);
    const isListeningRef = useRef(false);
    const onTranscriptRef = useRef(onTranscript);

    // Update ref when prop changes
    useEffect(() => {
        onTranscriptRef.current = onTranscript;
    }, [onTranscript]);

    useEffect(() => {
        // Check if browser supports Speech Recognition
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

        if (!SpeechRecognition) {
            setIsSupported(false);
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;

        // Set language based on prop
        recognition.lang = language === 'hi' ? 'hi-IN' : 'en-US';

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        recognition.onresult = (event: any) => {
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcriptPart = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcriptPart + ' ';
                } else {
                    interimTranscript += transcriptPart;
                }
            }

            const fullTranscript = finalTranscript || interimTranscript;
            setTranscript(fullTranscript);
            // Call the latest callback from ref
            if (onTranscriptRef.current) {
                onTranscriptRef.current(fullTranscript);
            }
        };

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        recognition.onerror = (event: any) => {
            console.error('Speech recognition error:', event.error);
            if (event.error === 'no-speech') {
                return;
            }
            setIsRecording(false);
            isListeningRef.current = false;
        };

        recognition.onend = () => {
            // If user still wants to record, restart
            if (isListeningRef.current) {
                try {
                    recognition.start();
                } catch (e) {
                    console.error('Failed to restart recognition:', e);
                    setIsRecording(false);
                    isListeningRef.current = false;
                }
            } else {
                setIsRecording(false);
            }
        };

        recognitionRef.current = recognition;

        return () => {
            // Only stop if we are unmounting or language changed
            isListeningRef.current = false;
            if (recognitionRef.current) {
                recognitionRef.current.stop();
            }
        };
    }, [language]); // Removed onTranscript from dependencies

    const startRecording = () => {
        if (recognitionRef.current) {
            setTranscript('');
            isListeningRef.current = true;
            try {
                recognitionRef.current.start();
                setIsRecording(true);
            } catch (e) {
                console.error('Failed to start recording:', e);
            }
        }
    };

    const stopRecording = () => {
        if (recognitionRef.current) {
            isListeningRef.current = false;
            recognitionRef.current.stop();
            setIsRecording(false);
        }
    };

    if (!isSupported) {
        return (
            <div className="p-4 bg-muted/50 border border-border rounded-lg text-center">
                <p className="text-sm text-muted-foreground">
                    Voice recording is not supported in this browser. Please use Chrome, Edge, or Safari.
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <motion.button
                        onClick={isRecording ? stopRecording : startRecording}
                        whileTap={{ scale: 0.95 }}
                        className={`relative p-4 rounded-full transition-all ${isRecording
                            ? 'bg-destructive hover:bg-destructive/90 shadow-lg shadow-destructive/50'
                            : 'bg-primary hover:bg-primary/90 shadow-lg shadow-primary/50'
                            }`}
                    >
                        {isRecording ? (
                            <>
                                <MicOff className="h-6 w-6 text-white" />
                                <motion.div
                                    className="absolute inset-0 rounded-full bg-destructive"
                                    animate={{ scale: [1, 1.2, 1] }}
                                    transition={{ repeat: Infinity, duration: 1.5 }}
                                    style={{ opacity: 0.3 }}
                                />
                            </>
                        ) : (
                            <Mic className="h-6 w-6 text-white" />
                        )}
                    </motion.button>

                    <div className="text-left">
                        <p className="text-sm font-semibold text-foreground">
                            {isRecording ? 'Recording...' : 'Voice Input'}
                        </p>
                        <p className="text-xs text-muted-foreground">
                            {isRecording ? 'Click to stop' : 'Click mic to start recording'}
                        </p>
                    </div>
                </div>

                {isRecording && (
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center gap-2"
                    >
                        <div className="flex gap-1">
                            {[0, 1, 2].map((i) => (
                                <motion.div
                                    key={i}
                                    className="w-1 bg-destructive rounded-full"
                                    animate={{ height: [8, 20, 8] }}
                                    transition={{
                                        repeat: Infinity,
                                        duration: 1,
                                        delay: i * 0.2,
                                    }}
                                />
                            ))}
                        </div>
                        <span className="text-xs text-destructive font-medium">LIVE</span>
                    </motion.div>
                )}
            </div>

            {transcript && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-4 bg-card border border-border rounded-lg"
                >
                    <div className="flex items-start justify-between mb-2">
                        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                            Transcript
                        </p>
                        {isRecording && (
                            <span className="text-xs text-primary animate-pulse">Listening...</span>
                        )}
                    </div>
                    <p className="text-sm text-foreground leading-relaxed">
                        {transcript}
                    </p>
                </motion.div>
            )}

            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Mic className="h-3 w-3" />
                <p>
                    Supports English and Hindi. Speak clearly for best results.
                </p>
            </div>
        </div>
    );
};
