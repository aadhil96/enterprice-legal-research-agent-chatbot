const InputBar = ({ currentMessage, setCurrentMessage, onSubmit }) => {

    const handleChange = (e) => {
        setCurrentMessage(e.target.value)
    }

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            onSubmit(e)
        }
    }

    return (
        <div className="p-4 bg-white border-t border-gray-100">
            <form onSubmit={onSubmit} className="max-w-3xl mx-auto">
                <div className="relative flex items-center">
                    {/* Main input container - Perplexity style */}
                    <div className="flex-1 flex items-center bg-gray-50 border border-gray-200 rounded-2xl px-4 py-3 focus-within:border-[#20b8cd] focus-within:ring-1 focus-within:ring-[#20b8cd]/20 transition-all">
                        {/* Attachment button */}
                        <button
                            type="button"
                            className="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors mr-2"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                            </svg>
                        </button>

                        {/* Input */}
                        <input
                            type="text"
                            placeholder="Ask about case law, statutes, legal concepts..."
                            value={currentMessage}
                            onChange={handleChange}
                            onKeyDown={handleKeyDown}
                            className="flex-1 bg-transparent text-gray-900 placeholder:text-gray-400 focus:outline-none text-base"
                        />

                        {/* Focus indicator */}
                        <button
                            type="button"
                            className="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors ml-2"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                            </svg>
                        </button>
                    </div>

                    {/* Submit button - Perplexity style */}
                    <button
                        type="submit"
                        disabled={!currentMessage.trim()}
                        className="ml-3 p-3 bg-[#20b8cd] hover:bg-[#1a9fb3] disabled:bg-gray-200 disabled:cursor-not-allowed text-white rounded-xl shadow-sm transition-all duration-200 hover:shadow-md"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                        </svg>
                    </button>
                </div>

                {/* Pro tip - Perplexity style */}
                <div className="flex items-center justify-center gap-4 mt-3 text-xs text-gray-400">
                    <span className="flex items-center gap-1">
                        <kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-500 font-mono">Enter</kbd>
                        to send
                    </span>
                    <span>•</span>
                    <span>Legal research assistance only - consult an attorney for legal advice</span>
                </div>
            </form>
        </div>
    )
}

export default InputBar