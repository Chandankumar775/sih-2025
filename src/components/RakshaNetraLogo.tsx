export const RakshaNetraLogo = () => {
    return (
        <div className="flex flex-col items-center gap-4 mb-8">
            <img 
                src="/media/logo.png" 
                alt="RakshaNetra Logo" 
                className="h-32 w-32 object-contain"
            />
            <div className="text-center">
                <h2 className="text-3xl font-bold text-gray-900">RAKSHA NETRA</h2>
                <p className="text-sm text-gray-600 mt-1">Ministry of Defence, Govt. of India</p>
            </div>
        </div>
    );
};
