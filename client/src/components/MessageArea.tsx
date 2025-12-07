import React from 'react';

const TypingIndicator = () => {
    return (
        <div className="flex items-center gap-1 py-1">
            <div className="w-2 h-2 bg-[#20b8cd] rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-[#20b8cd] rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-[#20b8cd] rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
    );
};

const SourceCard = ({ url }) => {
    let hostname = '';
    try {
        hostname = new URL(url).hostname.replace('www.', '');
    } catch {
        hostname = url;
    }

    return (
        <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-3 py-2 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-lg transition-colors group"
        >
            <div className="w-6 h-6 bg-gradient-to-br from-[#20b8cd] to-[#6366f1] rounded flex items-center justify-center flex-shrink-0">
                <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
            </div>
            <span className="text-sm text-gray-600 group-hover:text-gray-900 truncate">{hostname}</span>
            <svg className="w-4 h-4 text-gray-400 group-hover:text-gray-600 flex-shrink-0 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
        </a>
    );
};

const SearchProgress = ({ searchInfo }) => {
    if (!searchInfo || !searchInfo.stages || searchInfo.stages.length === 0) return null;

    return (
        <div className="mb-4 space-y-3">
            {/* Searching indicator */}
            {searchInfo.stages.includes('searching') && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                    <div className="w-4 h-4 border-2 border-[#20b8cd] border-t-transparent rounded-full animate-spin"></div>
                    <span>Searching legal sources for "{searchInfo.query}"</span>
                </div>
            )}

            {/* Sources */}
            {searchInfo.stages.includes('reading') && searchInfo.urls && searchInfo.urls.length > 0 && (
                <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                        <svg className="w-4 h-4 text-[#20b8cd]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span>Found {searchInfo.urls.length} sources</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {Array.isArray(searchInfo.urls) && searchInfo.urls.slice(0, 4).map((url, index) => (
                            <SourceCard key={index} url={url} />
                        ))}
                    </div>
                </div>
            )}

            {/* Error */}
            {searchInfo.stages.includes('error') && (
                <div className="flex items-center gap-2 text-sm text-red-500">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>Search encountered an error</span>
                </div>
            )}
        </div>
    );
};

const MessageArea = ({ messages }) => {
    return (
        <div className="flex-1 overflow-y-auto bg-white" style={{ minHeight: 0 }}>
            <div className="max-w-3xl mx-auto px-4 py-6">
                {messages.map((message) => (
                    <div key={message.id} className="mb-6">
                        {/* User message */}
                        {message.isUser ? (
                            <div className="flex justify-end">
                                <div className="max-w-[80%] bg-gray-100 text-gray-900 rounded-2xl rounded-br-md px-4 py-3">
                                    {message.content}
                                </div>
                            </div>
                        ) : (
                            /* AI message - Perplexity style */
                            <div className="space-y-3">
                                {/* AI indicator */}
                                <div className="flex items-center gap-2">
                                    <div className="w-6 h-6 bg-gradient-to-br from-[#20b8cd] to-[#6366f1] rounded-lg flex items-center justify-center">
                                        <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
                                        </svg>
                                    </div>
                                    <span className="text-sm font-medium text-gray-700">LexAI</span>
                                </div>

                                {/* Search progress */}
                                {message.searchInfo && (
                                    <SearchProgress searchInfo={message.searchInfo} />
                                )}

                                {/* Content */}
                                <div className="text-gray-800 leading-relaxed whitespace-pre-wrap pl-8">
                                    {message.isLoading ? (
                                        <TypingIndicator />
                                    ) : (
                                        message.content || <span className="text-gray-400 italic">Preparing response...</span>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default MessageArea;