import Link from "next/link";

interface Article {
  id: string;
  title: string;
  subtitle?: string;
  summary?: string;
  category?: string;
  ai_model?: string;
}

export default async function Home({ params }: { params: { lang: string } }) {
  let articles: Article[] = [];
  const lang = params.lang || "en";

  try {
    // Fetch data from the Go backend, passing language code
    const res = await fetch(`http://localhost:8080/api/v1/articles?lang=${lang}`, {
      cache: "no-store", 
    });
    
    if (res.ok) {
      articles = await res.json();
    } else {
      console.error("Failed to fetch articles:", res.statusText);
    }
  } catch (error) {
    console.error("Error connecting to Go backend API:", error);
  }

  // Gracefully handle empty state if the database is empty or backend is offline
  if (!articles || articles.length === 0) {
    return (
      <div className="py-20 text-center flex flex-col items-center border-t border-b border-nyt-border mt-8">
        <h2 className="font-playfair text-3xl mb-4 pt-12">The Presses are Stopped.</h2>
        <p className="font-inter text-nyt-gray pb-12">
          No published articles found. Run the Python Photographer & Journalist AI to generate content.
        </p>
      </div>
    );
  }

  const heroArticle = articles[0];
  const secondaryArticles = articles.slice(1);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
      {/* Front Page Primary Article */}
      <section className="lg:col-span-3">
        <article className="border-b border-nyt-border pb-8 mb-8">
          <Link href={`/${lang}/article/${heroArticle.id}`}>
            <h2 className="font-playfair text-4xl lg:text-5xl font-bold leading-tight hover:text-gray-700 transition-colors">
              {heroArticle.title}
            </h2>
          </Link>
          <div className="my-3 flex items-center gap-2">
            <span className="text-xs uppercase tracking-wider font-semibold border border-black px-2 py-0.5">
              {heroArticle.category || "General"}
            </span>
            <span className="text-xs text-nyt-gray flex items-center gap-1">
              <span className="w-2 h-2 bg-black rounded-full inline-block"></span>
              {heroArticle.ai_model || "AI Generated"}
            </span>
          </div>
          {heroArticle.subtitle && (
            <h3 className="font-playfair text-xl italic text-gray-800 mb-4">
              {heroArticle.subtitle}
            </h3>
          )}
          {heroArticle.summary && (
            <p className="font-inter text-lg leading-relaxed text-gray-900">
              {heroArticle.summary}
            </p>
          )}
        </article>

        {/* Secondary Articles Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {secondaryArticles.map((article) => (
            <article key={article.id} className="border-t border-nyt-border pt-4">
              <Link href={`/${lang}/article/${article.id}`}>
                <h4 className="font-playfair text-2xl font-bold mb-2 hover:text-gray-700 transition-colors">
                  {article.title}
                </h4>
              </Link>
              {article.subtitle && (
                <h5 className="font-playfair italic text-sm text-gray-800 mb-2">
                  {article.subtitle}
                </h5>
              )}
              {article.summary && (
                <p className="font-inter text-sm text-gray-700 line-clamp-3">
                  {article.summary}
                </p>
              )}
            </article>
          ))}
        </div>
      </section>

      {/* Sidebar: Trending Topics */}
      <aside className="lg:col-span-1 border-l pl-0 lg:pl-6 border-nyt-border">
        <h3 className="uppercase tracking-widest text-xs font-bold border-b-2 border-black pb-2 mb-4">
          Trending Topics
        </h3>
        <ul className="space-y-4 text-nyt-gray font-inter text-sm">
          <li>API Integration Connected ({lang.toUpperCase()}).</li>
          <li>Awaiting Trends...</li>
        </ul>
      </aside>
    </div>
  );
}
