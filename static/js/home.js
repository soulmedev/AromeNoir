function scrollToProducts() {
    document.getElementById('products').scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
    });
}

const observerOptions = {
    threshold: 0.15,
    rootMargin: '0px 0px -80px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
            setTimeout(() => {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }, index * 120);
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.product-card, .feature-card');
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(60px)';
        card.style.transition = 'opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1), transform 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
        observer.observe(card);
    });
});

let lastScrollY = 0;
let ticking = false;

function updateParallax() {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero-content');
    
    if (hero && scrolled < window.innerHeight) {
        hero.style.transform = `translateY(${scrolled * 0.4}px)`;
        hero.style.opacity = Math.max(0, 1 - scrolled / 600);
    }
    
    ticking = false;
}

window.addEventListener('scroll', () => {
    lastScrollY = window.pageYOffset;
    
    if (!ticking) {
        window.requestAnimationFrame(updateParallax);
        ticking = true;
    }
});

