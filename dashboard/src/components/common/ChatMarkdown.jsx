import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

/**
 * Renders AI assistant chat content as actual formatted markdown (tables,
 * headings, bold, lists) instead of raw `**`/`|`/`###` syntax, styled to fit
 * inside a colored chat bubble. `variant` picks the color scheme so text,
 * borders, and table rules stay legible against that bubble's background.
 */
export default function ChatMarkdown({ content, variant = 'assistant' }) {
  const isUser = variant === 'user';
  const isError = variant === 'error';

  const borderColor = isUser ? 'border-white/30' : isError ? 'border-red-200' : 'border-gray-300';
  const headerBg = isUser ? 'bg-white/10' : isError ? 'bg-red-100' : 'bg-gray-200';
  const rowAltBg = isUser ? 'even:bg-white/5' : isError ? 'even:bg-red-100/50' : 'even:bg-gray-50';
  const linkColor = isUser ? 'text-white underline' : 'text-sleepsia-700 underline hover:text-sleepsia-800';
  const codeBg = isUser ? 'bg-white/15' : 'bg-gray-200';

  return (
    <div className="text-sm leading-relaxed [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          p: ({ children }) => <p className="my-2 whitespace-pre-wrap">{children}</p>,
          strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
          em: ({ children }) => <em className="italic">{children}</em>,
          h1: ({ children }) => <h3 className="text-base font-bold mt-3 mb-1.5">{children}</h3>,
          h2: ({ children }) => <h3 className="text-base font-bold mt-3 mb-1.5">{children}</h3>,
          h3: ({ children }) => <h4 className="text-sm font-bold mt-3 mb-1">{children}</h4>,
          ul: ({ children }) => <ul className="list-disc pl-5 my-2 space-y-0.5">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal pl-5 my-2 space-y-0.5">{children}</ol>,
          li: ({ children }) => <li>{children}</li>,
          a: ({ children, href }) => (
            <a href={href} target="_blank" rel="noopener noreferrer" className={linkColor}>
              {children}
            </a>
          ),
          code: ({ children }) => (
            <code className={`${codeBg} rounded px-1 py-0.5 text-xs font-mono`}>{children}</code>
          ),
          pre: ({ children }) => (
            <pre className={`${codeBg} rounded-lg p-3 my-2 overflow-x-auto text-xs font-mono`}>{children}</pre>
          ),
          blockquote: ({ children }) => (
            <blockquote className={`border-l-4 ${borderColor} pl-3 my-2 italic opacity-90`}>
              {children}
            </blockquote>
          ),
          hr: () => <hr className={`my-3 ${borderColor}`} />,
          table: ({ children }) => (
            <div className={`my-3 overflow-x-auto rounded-lg border ${borderColor}`}>
              <table className="min-w-full text-xs border-collapse">{children}</table>
            </div>
          ),
          thead: ({ children }) => <thead className={headerBg}>{children}</thead>,
          tbody: ({ children }) => <tbody>{children}</tbody>,
          tr: ({ children }) => <tr className={`border-b ${borderColor} ${rowAltBg}`}>{children}</tr>,
          th: ({ children }) => (
            <th className={`px-3 py-2 text-left font-semibold border ${borderColor}`}>{children}</th>
          ),
          td: ({ children }) => <td className={`px-3 py-2 align-top border ${borderColor}`}>{children}</td>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
