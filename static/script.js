document.addEventListener("DOMContentLoaded", () => {
    // Smooth Scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener("click", function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute("href")).scrollIntoView({
                behavior: "smooth"
            });
        });
    });

    // Start Camera for Demo
    window.startCamera = function () {
        const video = document.getElementById("video");
        if (navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(stream => {
                    video.srcObject = stream;
                })
                .catch(error => {
                    console.error("Error accessing the camera:", error);
                });
        } else {
            alert("Your browser does not support camera access.");
        }
    };

    // Fade-in Effect on Scroll
    const sections = document.querySelectorAll("section");
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = 1;
                entry.target.style.transform = "translateY(0)";
            }
        });
    }, { threshold: 0.2 });
    
    sections.forEach(section => {
        section.style.opacity = 0;
        section.style.transform = "translateY(50px)";
        observer.observe(section);
    });

});
