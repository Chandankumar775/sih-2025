interface CyberCheckboxProps {
    checked: boolean;
    onChange: (checked: boolean) => void;
    label?: string;
}

export const CyberCheckbox = ({ checked, onChange, label }: CyberCheckboxProps) => {
    return (
        <div className="checkbox-wrapper" onClick={() => onChange(!checked)}>
            <input
                type="checkbox"
                checked={checked}
                onChange={(e) => onChange(e.target.checked)}
            />
            <div className="checkmark">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path
                        d="M20 6L9 17L4 12"
                        strokeWidth="3"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />
                </svg>
            </div>
            {label && <div className="label text-sm">{label}</div>}
        </div>
    );
};
