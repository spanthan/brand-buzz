export function LoadingOverlay() {
    return (
      <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center pointer-events-none">
        <div className="bg-white text-black p-6 rounded-lg shadow-xl z-50 pointer-events-auto">
          <div className="border-4 border-pink-500 border-t-transparent rounded-full w-12 h-12 animate-spin"></div>
        </div>
      </div>
    );
  }