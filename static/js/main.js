lucide.createIcons();
document.getElementById("year").textContent = new Date().getFullYear();
document.querySelectorAll(".service-card, .project-card, .testimonial-card").forEach((card) => {
  card.style.opacity = "0";
  card.style.transform = "translateY(14px)";
});
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.style.transition = "opacity .5s ease, transform .5s ease";
      entry.target.style.opacity = "1";
      entry.target.style.transform = "translateY(0)";
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.16 });
document.querySelectorAll(".service-card, .project-card, .testimonial-card").forEach((card) => observer.observe(card));
