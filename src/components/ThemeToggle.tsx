import { useEffect, useState } from "react";

export const ThemeToggle = () => {
    const [isDark, setIsDark] = useState(true);

    useEffect(() => {
        // Check local storage or system preference
        const storedTheme = localStorage.getItem("theme");
        const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

        if (storedTheme === "dark" || (!storedTheme && systemPrefersDark)) {
            setIsDark(true);
            document.documentElement.classList.add("dark");
        } else {
            setIsDark(false);
            document.documentElement.classList.remove("dark");
        }
    }, []);

    const toggleTheme = () => {
        const newIsDark = !isDark;
        setIsDark(newIsDark);

        if (newIsDark) {
            document.documentElement.classList.add("dark");
            localStorage.setItem("theme", "dark");
        } else {
            document.documentElement.classList.remove("dark");
            localStorage.setItem("theme", "light");
        }
    };

    return (
        <div className="theme-toggle-container scale-50 origin-right">
            <input
                type="checkbox"
                name="theme-checkbox"
                id="theme-checkbox"
                className="theme-toggle-checkbox"
                checked={isDark}
                onChange={toggleTheme}
            />
            <label htmlFor="theme-checkbox" className="theme-toggle-label"></label>
        </div>
    );
};
