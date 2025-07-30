import React, { useEffect } from "react";

function TikTokEmbedComponent() {
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://www.tiktok.com/embed.js";
    script.async = true;
    document.body.appendChild(script);
    return () => {
      document.body.removeChild(script);
    };
  }, []);

  return (
    <div className="rounded-2xl overflow-hidden bg-white border-2 border-white shadow-lg max-w-[340px]">
        <div
        dangerouslySetInnerHTML={{
            __html: `
            <blockquote 
                class="tiktok-embed" 
                cite="https://www.tiktok.com/@sarahpalmyra/video/7086537682649697578" 
                data-video-id="7086537682649697578" 
                style="max-width: 325px; min-width: 325px;">
                <section>
                <a target="_blank" title="@sarahpalmyra" href="https://www.tiktok.com/@sarahpalmyra?refer=embed">
                    @sarahpalmyra
                </a> How many likes will convince Cerave to bring this to the US 👀 
                <a title="skincare" target="_blank" href="https://www.tiktok.com/tag/skincare?refer=embed">#skincare</a> 
                <a title="cleanserreview" target="_blank" href="https://www.tiktok.com/tag/cleanserreview?refer=embed">#cleanserreview</a> 
                <a title="cerave" target="_blank" href="https://www.tiktok.com/tag/cerave?refer=embed">#cerave</a> 
                <a title="oilcleansing" target="_blank" href="https://www.tiktok.com/tag/oilcleansing?refer=embed">#oilcleansing</a> 
                <a target="_blank" title="♬ Quirky - Oleg Kirilkov" href="https://www.tiktok.com/music/Quirky-6770511259797293058?refer=embed">
                    ♬ Quirky - Oleg Kirilkov
                </a>
                </section>
            </blockquote>
            `,
        }}
        />
    </div>
  );
}

const TikTokEmbed = React.memo(TikTokEmbedComponent);
export default TikTokEmbed;
