import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export const LanguageSwitcher = () => {
    const { i18n } = useTranslation();
    const [isOpen, setIsOpen] = useState(false);

    const languages = [
        { code: 'en', name: 'English', flag: '🇬🇧' },
        { code: 'hi', name: 'हिंदी', flag: '🇮🇳' },
    ];

    const currentLanguage = languages.find(lang => lang.code === i18n.language) || languages[0];

    const changeLanguage = (code: string) => {
        i18n.changeLanguage(code);
        setIsOpen(false);
    };

    return (
        <div className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 border border-white/20 transition-all text-white"
            >
                <Globe className="h-4 w-4" />
                <span className="text-sm font-medium">{currentLanguage.flag} {currentLanguage.name}</span>
            </button>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="absolute top-full right-0 mt-2 w-40 rounded-lg bg-card border border-border shadow-xl overflow-hidden z-50"
                    >
                        {languages.map((lang) => (
                            <button
                                key={lang.code}
                                onClick={() => changeLanguage(lang.code)}
                                className={`w-full flex items-center gap-3 px-4 py-3 text-sm transition-colors ${i18n.language === lang.code
                                        ? 'bg-primary/20 text-primary font-semibold'
                                        : 'hover:bg-muted text-foreground'
                                    }`}
                            >
                                <span className="text-lg">{lang.flag}</span>
                                <span>{lang.name}</span>
                            </button>
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};
