import Link from 'next/link';
import { notFound } from 'next/navigation';

interface Article {
  id: string;
  title: string;
  subtitle?: string;
  summary?: string;
  content: string;
  category?: string;
  ai_model?: string;
  published_at?: string;
}

export default async function ArticlePage({ params }: { params: Promise<{ lang: string, id: string }> }) {
  const { lang, id } = await params;
  
  let article: Article | null = null;
  
  try {
    const res = await fetch(`http://localhost:8080/api/v1/articles/${id}?lang=${lang}`, {
      cache: "no-store", 
    });
    
    if (res.ok) {
      article = await res.json();
    }
  } catch (error) {
    console.error("Error fetching article:", error);
  }
  
  if (!article) {
    notFound();
  }
  
  return (
    <article className="max-w-3xl mx-auto py-12 px-4">
      <Link href={`/${lang}`} className="text-sm uppercase tracking-widest font-bold hover:underline mb-8 inline-block">
        ← Back to front page
      </Link>
      
      <header className="mb-10 text-center border-b border-nyt-border pb-8">
        <div className="mb-4 flex items-center justify-center gap-2">
          <span className="text-xs uppercase tracking-wider font-semibold border border-black px-2 py-0.5">
            {article.category || "General"}
          </span>
          <span className="text-xs text-nyt-gray flex items-center gap-1">
            <span className="w-2 h-2 bg-black rounded-full inline-block"></span>
            {article.ai_model || "AI Generated"} • {new Date(article.published_at || Date.now()).toLocaleDateString()}
          </span>
        </div>
        
        <h1 className="font-playfair text-4xl lg:text-5xl font-bold leading-tight mb-4">
          {article.title}
        </h1>
        
        {article.subtitle && (
          <h2 className="font-playfair text-2xl italic text-gray-700">
            {article.subtitle}
          </h2>
        )}
      </header>
      
      <div className="font-inter text-lg leading-relaxed text-gray-900 space-y-6">
        {article.content.split('\\n\\n').map((paragraph, idx) => {
          if (paragraph.startsWith('#')) {
            const hLevel = paragraph.match(/^#+/)?.[0].length || 1;
            const text = paragraph.replace(/^#+\\s*/, '').replace(/\\*\\*/g, '');
            if (hLevel === 1 || hLevel === 2) {
              return <h2 key={idx} className="font-playfair text-3xl font-bold mt-8 mb-4">{text}</h2>;
            }
            return <h3 key={idx} className="font-playfair text-2xl font-bold mt-6 mb-3">{text}</h3>;
          }
          const formattedText = paragraph.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
          return <p key={idx} dangerouslySetInnerHTML={{ __html: formattedText }}></p>;
        })}
      </div>
    </article>
  );
}
