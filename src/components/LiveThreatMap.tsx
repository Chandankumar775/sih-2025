import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Icon } from 'leaflet';
import { motion } from 'framer-motion';
import { Shield, AlertTriangle, Radio } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icon in React Leaflet
const DefaultIcon = new Icon({
    iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

// Custom icons for different threat levels
const criticalIcon = new Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

const highIcon = new Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

const mediumIcon = new Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

// Mock data for incidents across India
const incidents = [
    { id: 1, position: [28.6139, 77.2090], title: "Suspicious Signal", location: "New Delhi", severity: "critical", type: "Signal Intercept" }, // Delhi
    { id: 2, position: [19.0760, 72.8777], title: "Unauthorized Access", location: "Mumbai Naval Base", severity: "high", type: "Network Breach" }, // Mumbai
    { id: 3, position: [34.0837, 74.7973], title: "Border Intrusion Alert", location: "Srinagar", severity: "critical", type: "Physical Security" }, // Srinagar
    { id: 4, position: [13.0827, 80.2707], title: "Data Exfiltration", location: "Chennai", severity: "medium", type: "Malware" }, // Chennai
    { id: 5, position: [22.5726, 88.3639], title: "Phishing Campaign", location: "Kolkata", severity: "high", type: "Email Threat" }, // Kolkata
    { id: 6, position: [26.9124, 75.7873], title: "Drone Sighting", location: "Jaipur", severity: "medium", type: "Aerial Surveillance" }, // Jaipur
    { id: 7, position: [31.6340, 74.8723], title: "Comms Jamming", location: "Amritsar", severity: "critical", type: "Electronic Warfare" }, // Amritsar
    { id: 8, position: [17.3850, 78.4867], title: "Server DDoS", location: "Hyderabad", severity: "medium", type: "Cyber Attack" }, // Hyderabad
];

export const LiveThreatMap = () => {
    return (
        <div className="relative h-[500px] w-full rounded-xl overflow-hidden border border-white/10 shadow-2xl">
            {/* Overlay UI */}
            <div className="absolute top-4 right-4 z-[1000] bg-black/80 backdrop-blur-md p-4 rounded-lg border border-white/10">
                <div className="flex items-center gap-2 mb-2">
                    <Radio className="h-4 w-4 text-destructive animate-pulse" />
                    <span className="text-xs font-bold text-white uppercase tracking-wider">Live Threat Feed</span>
                </div>
                <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs text-gray-300">
                        <span className="w-2 h-2 rounded-full bg-red-500"></span>
                        Critical ({incidents.filter(i => i.severity === 'critical').length})
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-300">
                        <span className="w-2 h-2 rounded-full bg-orange-500"></span>
                        High ({incidents.filter(i => i.severity === 'high').length})
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-300">
                        <span className="w-2 h-2 rounded-full bg-yellow-500"></span>
                        Medium ({incidents.filter(i => i.severity === 'medium').length})
                    </div>
                </div>
            </div>

            <MapContainer
                center={[22.5937, 78.9629]}
                zoom={5}
                scrollWheelZoom={false}
                style={{ height: '100%', width: '100%', background: '#0a0a0a' }}
            >
                {/* Dark Theme Map Tiles */}
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />

                {incidents.map((incident) => (
                    <Marker
                        key={incident.id}
                        position={incident.position as [number, number]}
                        icon={
                            incident.severity === 'critical' ? criticalIcon :
                                incident.severity === 'high' ? highIcon : mediumIcon
                        }
                    >
                        <Popup className="custom-popup">
                            <div className="p-2 min-w-[200px]">
                                <div className="flex items-center justify-between mb-2">
                                    <span className={`text-xs font-bold px-2 py-0.5 rounded border ${incident.severity === 'critical' ? 'bg-red-500/10 text-red-500 border-red-500/20' :
                                        incident.severity === 'high' ? 'bg-orange-500/10 text-orange-500 border-orange-500/20' :
                                            'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'
                                        }`}>
                                        {incident.severity.toUpperCase()}
                                    </span>
                                    <span className="text-xs text-gray-500">Just now</span>
                                </div>
                                <h3 className="font-bold text-gray-900 text-sm mb-1">{incident.title}</h3>
                                <p className="text-xs text-gray-600 mb-2">{incident.location}</p>
                                <div className="text-xs font-mono bg-gray-100 p-1 rounded text-gray-700">
                                    Type: {incident.type}
                                </div>
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </div>
    );
};
