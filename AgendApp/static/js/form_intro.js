        const progressBar = document.getElementById('progress-bar');
        const counter = document.getElementById('counter');
        const intro = document.getElementById('intro-screen');
        const main = document.getElementById('main-content');

        function marcarCambiandoFecha() {
            sessionStorage.setItem('saltarIntro', 'true');
        }

        window.onload = function() {
            if (sessionStorage.getItem('saltarIntro') === 'true') {
                intro.style.display = 'none';
                main.classList.add('show-content');
                sessionStorage.removeItem('saltarIntro');
            } else {
                ejecutarIntro();
            }
        };

        function ejecutarIntro() {
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.floor(Math.random() * 15) + 10;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                    setTimeout(() => {
                        intro.classList.add('fade-out');
                        setTimeout(() => {
                            intro.style.display = 'none';
                            main.classList.add('show-content');
                        }, 800);
                    }, 400);
                }
                progressBar.style.width = progress + '%';
                counter.innerText = progress + '%';
            }, 150);
        }