import { Star } from 'lucide-react';

interface Testimonial {
  name: string;
  profession: string;
  avatarInitials: string;
  avatarBg: string;
  review: string;
  rating: number;
}

export default function TestimonialsSection() {
  const testimonials: Testimonial[] = [
    {
      name: 'Rajesh Patel',
      profession: 'E-commerce Business Owner (Mumbai)',
      avatarInitials: 'RP',
      avatarBg: 'from-blue-650 to-indigo-650',
      review: 'TAXORA optimized my salary structure and let-out property. Saved over ₹1.2 Lakhs in tax u/s 10(13A) and 24b legally!',
      rating: 5
    },
    {
      name: 'Ananya Rao',
      profession: 'Senior Software Engineer (Bengaluru)',
      avatarInitials: 'AR',
      avatarBg: 'from-teal-650 to-emerald-650',
      review: 'The AI CA parsed my Form 16 and investment statements in seconds. Unbelievably fast, detailed, and 100% compliant.',
      rating: 5
    },
    {
      name: 'Vikram Malhotra',
      profession: 'Freelance Design Consultant (Delhi)',
      avatarInitials: 'VM',
      avatarBg: 'from-purple-650 to-pink-650',
      review: 'Running my business, tax planning is always a headache. This dashboard compared regimes and gave me clear audit check logs.',
      rating: 5
    },
    {
      name: 'Priya Sharma',
      profession: 'Marketing Director (Hyderabad)',
      avatarInitials: 'PS',
      avatarBg: 'from-indigo-650 to-sky-650',
      review: 'Filing capital gains after Budget 2024 was confusing. The chatbot cleared the 12.5% LTCG rules with exact Act citations.',
      rating: 5
    },
    {
      name: 'Amit Verma',
      profession: 'Tech Startup Founder (Pune)',
      avatarInitials: 'AV',
      avatarBg: 'from-orange-600 to-red-650',
      review: 'Highly recommend the tax slab optimizer. It showed me exactly how much I could save by shifting to the New Regime.',
      rating: 5
    }
  ];

  // Duplicate the list of testimonials to ensure seamless looping in marquee
  const marqueeList = [...testimonials, ...testimonials];

  return (
    <section className="w-full py-16 px-6 md:px-12 relative flex flex-col items-center justify-center overflow-hidden">
      {/* Title Header */}
      <div className="text-center flex flex-col items-center gap-3 max-w-xl mb-16 relative z-10">
        <span className="text-xs font-semibold tracking-wider text-teal-400 uppercase">CLIENT TESTIMONIALS</span>
        <h2 className="text-3xl md:text-4xl font-bold text-white tracking-tight">
          Loved by taxpayers and CAs alike
        </h2>
        <p className="text-sm text-slate-400 leading-relaxed mt-1">
          Hear from individuals, business owners, and tax professionals who legally minimized their tax liability using TAXORA.
        </p>
      </div>

      {/* Marquee Track Container */}
      <div className="w-full max-w-5xl relative overflow-hidden z-10 py-4">
        
        {/* Soft fading edges left & right */}
        <div className="absolute left-0 top-0 bottom-0 w-24 bg-gradient-to-r from-slate-950 to-transparent z-20 pointer-events-none" />
        <div className="absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-slate-950 to-transparent z-20 pointer-events-none" />

        {/* Scrolling track */}
        <div className="animate-marquee gap-6 flex">
          {marqueeList.map((test, idx) => (
            <div
              key={idx}
              className="w-[280px] sm:w-[320px] shrink-0 p-6 bg-slate-900/25 border border-slate-800/60 rounded-2xl flex flex-col justify-between gap-5 backdrop-blur-md hover:border-blue-500/20 transition-all duration-300 select-none group"
            >
              {/* Star Rating & Quote block */}
              <div className="flex flex-col gap-3">
                <div className="flex gap-0.5">
                  {Array.from({ length: test.rating }).map((_, sIdx) => (
                    <Star key={sIdx} className="h-3.5 w-3.5 fill-yellow-500 text-yellow-500" />
                  ))}
                </div>
                <p className="text-xs text-slate-300 leading-relaxed text-left">
                  "{test.review}"
                </p>
              </div>

              {/* User profile details */}
              <div className="flex items-center gap-3 border-t border-slate-800/60 pt-4">
                {/* Initials avatar circle */}
                <div className={`h-9 w-9 rounded-full bg-gradient-to-tr ${test.avatarBg} flex items-center justify-center text-xs font-bold text-white shrink-0 shadow`}>
                  {test.avatarInitials}
                </div>
                <div className="flex flex-col text-left truncate">
                  <span className="text-xs font-bold text-white">{test.name}</span>
                  <span className="text-[10px] text-slate-500 font-medium truncate mt-0.5">{test.profession}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

      </div>
    </section>
  );
}
