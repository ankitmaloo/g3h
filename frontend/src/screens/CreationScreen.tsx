
import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Upload,
    Download,
    Image as ImageIcon,
    FileText,
    XCircle,
    RefreshCw,
    Sparkles,
    ScanLine,
    Layers,
    MoveRight
} from "lucide-react";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { generateImage } from "@/services/api";

const PixelGenerationEffect = () => {
    const gridSize = 16;
    const cells = Array.from({ length: gridSize * gridSize });

    return (
        <div
            className="absolute inset-0 z-20 grid pointer-events-none mix-blend-overlay"
            style={{
                gridTemplateColumns: `repeat(${gridSize}, 1fr)`,
                gridTemplateRows: `repeat(${gridSize}, 1fr)`
            }}
        >
            {cells.map((_, i) => (
                <motion.div
                    key={i}
                    initial={{ opacity: 0 }}
                    animate={{
                        opacity: [0, 0.4, 0.8, 0.4, 0],
                        backgroundColor: [
                            "transparent",
                            "rgba(249, 115, 22, 0.1)", // orange
                            "rgba(244, 63, 94, 0.2)", // rose
                            "transparent"
                        ]
                    }}
                    transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        delay: Math.random() * 2,
                        ease: "easeOut"
                    }}
                    className="border-[0.5px] border-white/5"
                />
            ))}
        </div>
    );
};

// Premium background with subtle moving gradients - ORANGE/ROSE THEME
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

export default function CreationScreen() {
    const [sourceImages, setSourceImages] = useState<File[]>([]);
    const [previewUrls, setPreviewUrls] = useState<string[]>([]);
    const [activeIndex, setActiveIndex] = useState<number>(0);
    const [secretData, setSecretData] = useState("");
    const [isProcessing, setIsProcessing] = useState(false);
    const [isComplete, setIsComplete] = useState(false);
    const [generatedImageUrl, setGeneratedImageUrl] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        if (e.dataTransfer.files) {
            handleFiles(Array.from(e.dataTransfer.files));
        }
    };

    const handleFiles = (files: File[]) => {
        const remainingSlots = 5 - sourceImages.length;
        if (remainingSlots <= 0) return;

        const newFiles = files.slice(0, remainingSlots);
        const newUrls = newFiles.map(file => URL.createObjectURL(file));

        setSourceImages(prev => [...prev, ...newFiles]);
        setPreviewUrls(prev => [...prev, ...newUrls]);

        if (sourceImages.length === 0) {
            setActiveIndex(0);
        }

        setIsComplete(false);
    };

    const handleEmbed = async () => {
        if (sourceImages.length === 0) return;

        setIsProcessing(true);
        setIsComplete(false);
        setError(null);

        try {
            const generatedUrl = await generateImage(sourceImages, secretData);
            setGeneratedImageUrl(generatedUrl);
            setIsComplete(true);
        } catch (err) {
            console.error("Generation failed:", err);
            setError(err instanceof Error ? err.message : "Generation failed");
        } finally {
            setIsProcessing(false);
        }
    };

    const handleDownload = () => {
        const urlToDownload = isComplete && generatedImageUrl ? generatedImageUrl : previewUrls[activeIndex];
        if (!urlToDownload) return;

        const a = document.createElement("a");
        a.href = urlToDownload;
        a.download = `nexus_portrait_${Date.now()}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    };

    const reset = () => {
        setSourceImages([]);
        setPreviewUrls([]);
        setActiveIndex(0);
        setSecretData("");
        setIsComplete(false);
        setIsProcessing(false);
        setGeneratedImageUrl(null);
        setError(null);
    };

    const removeImage = (index: number, e: React.MouseEvent) => {
        e.stopPropagation();
        const newImages = sourceImages.filter((_, i) => i !== index);
        const newUrls = previewUrls.filter((_, i) => i !== index);

        setSourceImages(newImages);
        setPreviewUrls(newUrls);

        if (activeIndex >= newImages.length) {
            setActiveIndex(Math.max(0, newImages.length - 1));
        }
    };

    return (
        <div className="relative min-h-screen text-white p-8 font-sans overflow-x-hidden selection:bg-orange-500/30 selection:text-orange-100">
            <BackgroundEffects />

            <div className="relative z-10 max-w-7xl mx-auto h-full pt-12">

                {/* Header Section */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 1 }}
                    className="mb-12"
                >
                    <h1 className="text-6xl font-extralight tracking-tighter text-white mb-4">
                        Digital <span className="font-semibold bg-clip-text text-transparent bg-gradient-to-r from-orange-300 via-white to-orange-300 animate-gradient-x">Portrait</span>
                    </h1>
                    <p className="text-xl text-zinc-400 font-light max-w-2xl leading-relaxed">
                        Forge high-fidelity digital assets with cryptographically secure provenance.
                        <span className="opacity-50 mx-2">|</span>
                        <span className="text-orange-400/80 font-mono text-sm tracking-wide">V 4.0.1 BETA</span>
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">

                    {/* Left Panel: Studio Controls (Cols 1-5) */}
                    <motion.div
                        initial={{ opacity: 0, x: -50 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.8, delay: 0.2 }}
                        className="lg:col-span-5 space-y-8"
                    >
                        <div className="bg-zinc-900/40 backdrop-blur-2xl p-8 rounded-3xl border border-white/10 shadow-2xl relative overflow-hidden group">
                            {/* Panel Glow interactions */}
                            <div className="absolute top-0 right-0 p-32 bg-orange-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-orange-500/20 transition-all duration-700" />

                            {/* Section: Asset Library */}
                            <div className="space-y-6 relative">
                                <div className="flex justify-between items-end border-b border-white/5 pb-4">
                                    <Label className="text-zinc-400 text-[10px] uppercase tracking-[0.2em] font-medium flex items-center gap-2">
                                        <Layers size={14} /> Base Assets
                                    </Label>
                                    <span className="font-mono text-xs text-zinc-500">{sourceImages.length} of 5</span>
                                </div>

                                {/* Drag & Drop Zone */}
                                <div
                                    className={`
                                        relative group/upload h-40 rounded-xl border border-dashed transition-all duration-500 flex flex-col items-center justify-center cursor-pointer overflow-hidden
                                        ${sourceImages.length < 5
                                            ? 'border-zinc-700 hover:border-orange-400/50 bg-black/20 hover:bg-black/40'
                                            : 'border-zinc-800 opacity-50 cursor-not-allowed'}
                                    `}
                                    onDragOver={handleDragOver}
                                    onDrop={handleDrop}
                                    onClick={() => sourceImages.length < 5 && fileInputRef.current?.click()}
                                >
                                    <div className="absolute inset-0 bg-gradient-to-br from-orange-500/0 via-orange-500/0 to-orange-500/5 group-hover/upload:from-orange-500/5 transition-all duration-500" />

                                    <div className="relative z-10 flex flex-col items-center text-center space-y-3 p-4">
                                        <div className="p-3 rounded-full bg-zinc-900 ring-1 ring-white/10 group-hover/upload:scale-110 group-hover/upload:ring-orange-500/50 transition-all duration-300 shadow-lg">
                                            <Upload className="w-5 h-5 text-zinc-400 group-hover/upload:text-orange-400 transition-colors" />
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-zinc-300 group-hover/upload:text-white transition-colors">
                                                {sourceImages.length < 5 ? "Drop assets here" : "Library Full"}
                                            </p>
                                            <p className="text-xs text-zinc-600 mt-1">Supports PNG, JPG, WEBP</p>
                                        </div>
                                    </div>
                                    <input type="file" ref={fileInputRef} className="hidden" accept="image/*" multiple onChange={(e) => e.target.files && handleFiles(Array.from(e.target.files))} />
                                </div>

                                {/* Thumbnail Strip */}
                                <div className="h-16 flex gap-2">
                                    <AnimatePresence>
                                        {sourceImages.length > 0 && sourceImages.map((_, idx) => (
                                            <motion.div
                                                key={idx}
                                                initial={{ opacity: 0, scale: 0, width: 0 }}
                                                animate={{ opacity: 1, scale: 1, width: "auto" }}
                                                exit={{ opacity: 0, scale: 0, width: 0 }}
                                                className={`
                                                    relative aspect-square h-full rounded-lg overflow-hidden cursor-pointer border transition-all duration-300 group/thumb
                                                    ${activeIndex === idx
                                                        ? 'border-orange-400 shadow-[0_4px_12px_rgba(249,115,22,0.2)] scale-105 z-10'
                                                        : 'border-white/5 hover:border-white/20 hover:scale-105 opacity-60 hover:opacity-100'}
                                                `}
                                                onClick={() => setActiveIndex(idx)}
                                            >
                                                <img src={previewUrls[idx]} alt="" className="w-full h-full object-cover" />
                                                <button
                                                    onClick={(e) => removeImage(idx, e)}
                                                    className="absolute top-0.5 right-0.5 p-1 rounded-full bg-black/60 text-white opacity-0 group-hover/thumb:opacity-100 hover:bg-rose-500 transition-all duration-200"
                                                >
                                                    <XCircle size={10} />
                                                </button>
                                            </motion.div>
                                        ))}
                                    </AnimatePresence>
                                    {sourceImages.length > 0 && sourceImages.length < 5 && (
                                        <motion.button
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            onClick={() => fileInputRef.current?.click()}
                                            className="h-full aspect-square rounded-lg border border-dashed border-zinc-800 flex items-center justify-center text-zinc-600 hover:text-zinc-400 hover:border-zinc-600 transition-all"
                                        >
                                            <span className="text-xl font-light">+</span>
                                        </motion.button>
                                    )}
                                </div>
                            </div>

                            {/* Section: Metadata */}
                            <div className="space-y-4 pt-6 mt-8 border-t border-white/5">
                                <Label className="text-zinc-400 text-[10px] uppercase tracking-[0.2em] font-medium flex items-center gap-2">
                                    <ScanLine size={14} /> Embedded Metadata
                                </Label>
                                <div className="relative group/input">
                                    <div className="absolute inset-0 bg-orange-500/5 rounded-lg opacity-0 group-hover/input:opacity-100 transition-opacity duration-500 blur-sm" />
                                    <Textarea
                                        placeholder="// Enter provenance signature, checksum, or private key..."
                                        value={secretData}
                                        onChange={(e) => setSecretData(e.target.value)}
                                        className="relative min-h-[140px] bg-black/50 border-white/10 text-zinc-300 focus:border-orange-500/40 focus:ring-0 resize-none font-mono text-[13px] leading-relaxed backdrop-blur-sm p-4 rounded-xl transition-all duration-300 placeholder:text-zinc-700"
                                    />
                                    <div className="absolute bottom-3 right-3 text-[10px] text-zinc-600 font-mono flex items-center gap-2">
                                        <span className={`w-1.5 h-1.5 rounded-full ${secretData.length > 0 ? 'bg-orange-500 animate-pulse' : 'bg-zinc-800'}`} />
                                        {secretData.length} BYTES
                                    </div>
                                </div>
                            </div>

                            {/* Section: Action */}
                            <div className="pt-8">
                                {!isComplete ? (
                                    <Button
                                        onClick={handleEmbed}
                                        disabled={sourceImages.length === 0 || isProcessing}
                                        className="relative w-full h-14 bg-white text-black font-semibold tracking-wide transition-all duration-500 overflow-hidden group/btn hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                                    >
                                        <div className="absolute inset-0 bg-gradient-to-r from-orange-400 via-orange-200 to-orange-400 opacity-0 group-hover/btn:opacity-100 transition-opacity duration-500 mix-blend-color-dodge blur-lg" />
                                        <span className="relative z-10 flex items-center justify-center gap-3">
                                            {isProcessing ? (
                                                <>
                                                    <RefreshCw size={18} className="animate-spin" />
                                                    RENDERING PORTRAIT...
                                                </>
                                            ) : (
                                                <>
                                                    RENDER PORTRAIT <MoveRight size={18} className="group-hover/btn:translate-x-1 transition-transform" />
                                                </>
                                            )}
                                        </span>
                                    </Button>
                                ) : (
                                    <div className="flex flex-col gap-4">
                                        {error && (
                                            <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg text-sm">
                                                {error}
                                            </div>
                                        )}
                                        <div className="flex gap-4">
                                            <Button
                                                onClick={handleDownload}
                                                className="flex-1 h-14 bg-rose-600 hover:bg-rose-500 text-white font-bold tracking-wide shadow-[0_0_40px_rgba(225,29,72,0.3)] hover:shadow-[0_0_60px_rgba(225,29,72,0.5)] transition-all duration-300"
                                            >
                                                <Download className="mr-2 h-5 w-5" /> DOWNLOAD ASSET
                                            </Button>
                                            <Button
                                                onClick={() => { setIsProcessing(false); setIsComplete(false); setGeneratedImageUrl(null); setError(null); }}
                                                variant="outline"
                                                className="h-14 w-14 p-0 border-white/10 bg-white/5 hover:bg-white/10 hover:border-white/20 text-white rounded-xl"
                                            >
                                                <RefreshCw size={20} />
                                            </Button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </motion.div>

                    {/* Right Panel: Visualization (Cols 6-12) */}
                    <div className="lg:col-span-7 h-full min-h-[600px] flex flex-col">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 1, delay: 0.4 }}
                            className="relative flex-1 bg-black/40 rounded-[2rem] border border-white/10 overflow-hidden backdrop-blur-sm group/frame shadow-2xl flex items-center justify-center p-8"
                        >
                            {/* Decorative Frame Elements */}
                            <div className="absolute top-6 left-6 w-32 h-32 border-l border-t border-white/20 rounded-tl-3xl pointer-events-none" />
                            <div className="absolute bottom-6 right-6 w-32 h-32 border-r border-b border-white/20 rounded-br-3xl pointer-events-none" />
                            <div className="absolute top-6 right-6 text-[10px] font-mono text-zinc-600 tracking-widest uppercase">
                                Viewport 01
                            </div>

                            <AnimatePresence mode="wait">
                                {previewUrls.length === 0 ? (
                                    <motion.div
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        className="text-center space-y-6"
                                    >
                                        <div className="relative">
                                            <div className="absolute inset-0 bg-orange-500/20 blur-2xl rounded-full animate-pulse" />
                                            <div className="relative w-32 h-32 rounded-full bg-zinc-900/80 border border-white/10 flex items-center justify-center mx-auto backdrop-blur-md">
                                                <ImageIcon className="text-zinc-700 w-12 h-12" />
                                            </div>
                                        </div>
                                        <div>
                                            <p className="text-zinc-500 text-lg font-light tracking-wide">Studio Empty</p>
                                            <p className="text-zinc-700 text-sm mt-1">Upload an asset to begin</p>
                                        </div>
                                    </motion.div>
                                ) : (
                                    <motion.div
                                        key={isComplete && generatedImageUrl ? generatedImageUrl : previewUrls[activeIndex]}
                                        className="relative w-full h-full flex items-center justify-center"
                                        initial={{ opacity: 0, scale: 0.95, filter: "blur(10px)" }}
                                        animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
                                        exit={{ opacity: 0, scale: 1.05, filter: "blur(10px)" }}
                                        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
                                    >
                                        <div className={`
                                            relative max-h-full max-w-full transition-all duration-700
                                            ${isProcessing ? 'scale-95 opacity-80' : ''}
                                            ${isComplete ? 'scale-100' : ''}
                                        `}>
                                            <motion.img
                                                src={isComplete && generatedImageUrl ? generatedImageUrl : previewUrls[activeIndex]}
                                                alt="Target"
                                                className="max-h-[600px] w-auto h-auto object-contain rounded-lg shadow-2xl"
                                                animate={{
                                                    filter: isProcessing ? "blur(4px) brightness(0.6) contrast(1.1) grayscale(0.5)" : "blur(0px) brightness(1) contrast(1) grayscale(0)"
                                                }}
                                                transition={{ duration: 0.8 }}
                                            />

                                            {/* Effect Layers */}
                                            {isProcessing && <PixelGenerationEffect />}

                                            {isComplete && (
                                                <motion.div
                                                    initial={{ opacity: 0, scale: 0.8, y: 20 }}
                                                    animate={{ opacity: 1, scale: 1, y: 0 }}
                                                    transition={{ type: "spring", bounce: 0.4 }}
                                                    className="absolute -bottom-20 left-1/2 -translate-x-1/2 z-40"
                                                >
                                                    <div className="bg-rose-500 text-white px-6 py-3 rounded-full flex items-center gap-3 shadow-[0_10px_40px_rgba(225,29,72,0.5)] font-bold tracking-wide text-sm">
                                                        <Sparkles size={16} />
                                                        ASSET READY
                                                    </div>
                                                </motion.div>
                                            )}
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </motion.div>

                        {/* Status Bar */}
                        <div className="h-10 mt-4 flex items-center gap-6 text-[10px] font-mono text-zinc-600 uppercase tracking-widest px-4">
                            <span className="flex items-center gap-2">
                                <span className={`w-1.5 h-1.5 rounded-full ${isProcessing ? 'bg-amber-500 animate-bounce' : 'bg-rose-500'}`} />
                                SYSTEM {isProcessing ? 'BUSY' : 'READY'}
                            </span>
                            <span className="flex-1 h-px bg-zinc-900" />
                            <span>Latency: 12ms</span>
                            <span>Secure Connection</span>
                        </div>
                    </div>

                </div>
            </div >
        </div >
    );
}
