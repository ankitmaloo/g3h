
import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Scan,
    ShieldCheck,
    AlertTriangle,
    Upload,
    FileSearch,
    Terminal,
    Fingerprint,
    CheckCircle2,
    XCircle,
    Copy,
    Search
} from "lucide-react";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

// Premium background reused for consistency
const BackgroundEffects = () => (
    <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute inset-0 bg-zinc-950" />
        <motion.div
            animate={{
                scale: [1, 1.2, 1],
                opacity: [0.3, 0.5, 0.3],
                x: [-100, 100, -100],
                y: [-50, 50, -50]
            }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="absolute top-0 left-0 w-[800px] h-[800px] bg-orange-900/10 rounded-full blur-[120px] mix-blend-screen"
        />
        <motion.div
            animate={{
                scale: [1, 1.1, 1],
                opacity: [0.2, 0.4, 0.2],
                x: [100, -100, 100]
            }}
            transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
            className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-rose-900/10 rounded-full blur-[100px] mix-blend-screen"
        />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150 mix-blend-overlay" />
    </div>
);

// Scanning animation component
const ScannerBeam = () => (
    <div className="absolute inset-0 z-20 pointer-events-none overflow-hidden rounded-lg">
        <motion.div
            animate={{ top: ["0%", "100%", "0%"] }}
            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
            className="absolute left-0 right-0 h-1 bg-orange-400/50 shadow-[0_0_20px_rgba(249,115,22,0.5)] blur-[1px]"
        />
        <motion.div
            animate={{ top: ["0%", "100%", "0%"], opacity: [0, 1, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
            className="absolute left-0 right-0 h-32 bg-gradient-to-b from-orange-500/0 via-orange-500/10 to-orange-500/0"
        />
    </div>
);

export default function DetectionScreen() {
    const [image, setImage] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [isScanning, setIsScanning] = useState(false);
    const [scanComplete, setScanComplete] = useState(false);
    const [metadata, setMetadata] = useState<string | null>(null);

    // Simulate finding data
    const [verificationStep, setVerificationStep] = useState(0);

    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        if (e.dataTransfer.files?.[0]) {
            processFile(e.dataTransfer.files[0]);
        }
    };

    const processFile = (file: File) => {
        setImage(file);
        setPreviewUrl(URL.createObjectURL(file));
        setScanComplete(false);
        setMetadata(null);
        setVerificationStep(0);
    };

    const handleScan = () => {
        if (!image) return;
        setIsScanning(true);
        setVerificationStep(1);

        // Simulation timeline
        setTimeout(() => setVerificationStep(2), 1500); // Analyze structure
        setTimeout(() => setVerificationStep(3), 3000); // Extract payload
        setTimeout(() => {
            setIsScanning(false);
            setScanComplete(true);
            setMetadata("PROVENANCE_KEY_VERIFIED: 0x92f...a12b\nTIMESTAMP: 2024-12-06T19:42:00Z\nORIGIN: NEXUS_TERMINAL_ALPHA\nINTEGRITY: 100%");
        }, 4500);
    };

    const reset = () => {
        setImage(null);
        setPreviewUrl(null);
        setScanComplete(false);
        setMetadata(null);
        setVerificationStep(0);
    };

    return (
        <div className="relative min-h-screen text-white p-8 font-sans overflow-x-hidden selection:bg-orange-500/30 selection:text-orange-100">
            <BackgroundEffects />

            <div className="relative z-10 max-w-7xl mx-auto h-full pt-12">

                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 1 }}
                    className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6"
                >
                    <div>
                        <h1 className="text-5xl font-extralight tracking-tighter text-white mb-2">
                            Asset <span className="font-semibold text-orange-400">Verification</span>
                        </h1>
                        <p className="text-lg text-zinc-500 font-light">
                            Cryptographic analysis and provenance validation.
                        </p>
                    </div>
                </motion.div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">

                    {/* Left Panel: Input & Controls (Cols 1-5) */}
                    <motion.div
                        initial={{ opacity: 0, x: -50 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.8, delay: 0.2 }}
                        className="lg:col-span-5 space-y-6"
                    >
                        <div className="bg-zinc-900/40 backdrop-blur-2xl p-8 rounded-3xl border border-white/10 shadow-2xl relative overflow-hidden">

                            <Label className="text-zinc-400 text-[10px] uppercase tracking-[0.2em] font-medium flex items-center gap-2 mb-6">
                                <Search size={14} /> Source Material
                            </Label>

                            {/* Upload Area */}
                            <div
                                className={`
                                    relative h-64 rounded-2xl border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center cursor-pointer overflow-hidden group
                                    ${!image
                                        ? 'border-zinc-800 hover:border-orange-400/50 hover:bg-zinc-900/50'
                                        : 'border-orange-500 bg-zinc-950'}
                                `}
                                onDragOver={(e) => e.preventDefault()}
                                onDrop={handleDrop}
                                onClick={() => !isScanning && fileInputRef.current?.click()}
                            >
                                {!image ? (
                                    <div className="text-center space-y-4 p-6">
                                        <div className="w-16 h-16 rounded-full bg-zinc-900 flex items-center justify-center mx-auto ring-1 ring-white/10 group-hover:ring-orange-500/50 group-hover:scale-110 transition-all duration-300">
                                            <Upload className="w-6 h-6 text-zinc-500 group-hover:text-orange-400" />
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-white group-hover:text-orange-200">Drop asset to analyze</p>
                                            <p className="text-xs text-zinc-600 mt-1">Supports encoded PNG/WEBP</p>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="relative w-full h-full p-2">
                                        <img src={previewUrl!} alt="Preview" className="w-full h-full object-contain rounded-xl" />
                                        {!isScanning && (
                                            <div className="absolute inset-0 flex items-center justify-center bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <p className="text-xs text-white uppercase tracking-widest">Click to Change</p>
                                            </div>
                                        )}
                                        {isScanning && <ScannerBeam />}
                                    </div>
                                )}
                                <input type="file" ref={fileInputRef} className="hidden" accept="image/*" onChange={(e) => e.target.files && processFile(e.target.files[0])} disabled={isScanning} />
                            </div>

                            {/* Analysis Steps */}
                            <div className="mt-8 space-y-4">
                                {isScanning || scanComplete ? (
                                    <div className="space-y-3">
                                        <StepItem step={1} current={verificationStep} label="Initializing Scanner" />
                                        <StepItem step={2} current={verificationStep} label="Analyzing Steganographic Layer" />
                                        <StepItem step={3} current={verificationStep} label="Deciphering Payload" />
                                    </div>
                                ) : (
                                    <div className="h-32 flex items-center justify-center text-zinc-700 text-xs uppercase tracking-widest italic">
                                        Waiting for input...
                                    </div>
                                )}
                            </div>

                            <div className="pt-8 mt-4 border-t border-white/5">
                                {!scanComplete ? (
                                    <Button
                                        onClick={handleScan}
                                        disabled={!image || isScanning}
                                        className="w-full h-14 bg-white hover:bg-zinc-200 text-black font-semibold rounded-xl transition-all shadow-lg hover:shadow-orange-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {isScanning ? <span className="animate-pulse">SCANNING...</span> : "INITIATE SCAN"}
                                    </Button>
                                ) : (
                                    <Button onClick={reset} variant="outline" className="w-full h-14 border-zinc-700 hover:bg-zinc-800 text-zinc-300">
                                        ANALYZE ANOTHER ASSET
                                    </Button>
                                )}
                            </div>
                        </div>
                    </motion.div>

                    {/* Right Panel: Results (Cols 6-12) */}
                    <div className="lg:col-span-7 h-full min-h-[500px] flex flex-col">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 1, delay: 0.4 }}
                            className="relative flex-1 bg-black/40 rounded-[2rem] border border-white/10 overflow-hidden backdrop-blur-sm p-8 flex flex-col"
                        >
                            {/* Decorative Frame */}
                            <div className="absolute top-6 right-6 text-[10px] font-mono text-zinc-600 tracking-widest uppercase flex items-center gap-2">
                                <div className={`w-2 h-2 rounded-full ${scanComplete ? 'bg-rose-500' : 'bg-zinc-800'}`} />
                                Terminal 02
                            </div>

                            {!scanComplete ? (
                                <div className="flex-1 flex flex-col items-center justify-center text-zinc-600 space-y-6">
                                    <div className="w-24 h-24 rounded-full border border-zinc-800 flex items-center justify-center">
                                        <ShieldCheck size={32} className="opacity-20" />
                                    </div>
                                    <p className="font-mono text-xs uppercase tracking-widest">Awaiting Analysis Results</p>
                                </div>
                            ) : (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="flex-1 flex flex-col space-y-6"
                                >
                                    <div className="flex items-center gap-4 text-rose-500 border-b border-rose-500/20 pb-6">
                                        <div className="p-3 bg-rose-500/10 rounded-full">
                                            <ShieldCheck size={32} />
                                        </div>
                                        <div>
                                            <h3 className="text-xl font-bold text-white tracking-wide">VERIFICATION SUCCESSFUL</h3>
                                            <p className="text-rose-400 text-sm font-mono mt-1">Digital Signature Authenticated</p>
                                        </div>
                                    </div>

                                    <div className="flex-1 bg-black/50 rounded-xl border border-white/5 p-6 font-mono text-sm leading-7 text-zinc-300 overflow-y-auto">
                                        {metadata?.split('\n').map((line, i) => (
                                            <div key={i} className="flex gap-4">
                                                <span className="text-zinc-600 select-none">{String(i + 1).padStart(2, '0')}</span>
                                                <span className={line.includes('VERIFIED') ? 'text-emerald-400' : ''}>
                                                    {line}
                                                </span>
                                            </div>
                                        ))}
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="bg-zinc-900/50 p-4 rounded-lg border border-white/5">
                                            <p className="text-[10px] uppercase text-zinc-500 tracking-wider mb-1">Confidence Score</p>
                                            <p className="text-2xl text-white font-light">99.9%</p>
                                        </div>
                                        <div className="bg-zinc-900/50 p-4 rounded-lg border border-white/5">
                                            <p className="text-[10px] uppercase text-zinc-500 tracking-wider mb-1">Encryption</p>
                                            <p className="text-2xl text-white font-light">AES-256</p>
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                        </motion.div>
                    </div>

                </div>
            </div>
        </div>
    );
}

const StepItem = ({ step, current, label }: { step: number, current: number, label: string }) => {
    const isCompleted = current > step;
    const isActive = current === step;
    return (
        <div className={`flex items-center gap-3 text-sm transition-colors ${isActive ? 'text-orange-400' : isCompleted ? 'text-zinc-500' : 'text-zinc-700'}`}>
            <div className={`
                w-5 h-5 rounded-full flex items-center justify-center text-[10px] border
                ${isActive ? 'border-orange-400 bg-orange-400/10' : isCompleted ? 'border-zinc-700 bg-zinc-800' : 'border-zinc-800'}
            `}>
                {isCompleted ? <CheckCircle2 size={10} /> : step}
            </div>
            <span className="uppercase tracking-wide font-medium">{label}</span>
        </div>
    );
};
