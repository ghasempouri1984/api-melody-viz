/*!
* Start Bootstrap - Business Casual v7.0.9 (https://startbootstrap.com/theme/business-casual)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-business-casual/blob/master/LICENSE)
*/
// Highlights current date on contact page

/*
window.addEventListener('DOMContentLoaded', event => {
    const listHoursArray = document.body.querySelectorAll('.list-hours li');
    listHoursArray[new Date().getDay()].classList.add(('today'));
})
*/
/**/
function setCookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = `expires=${date.toUTCString()}`;
    document.cookie = `${name}=${value};${expires};path=/`;
}

function getCookie(name) {
    const cookieName = `${name}=`;
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookies = decodedCookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        if (cookie.indexOf(cookieName) === 0) {
            return cookie.substring(cookieName.length, cookie.length);
        }
    }
    return '';
}

// Utility to load stylesheet asynchronously
function loadStylesheetAsync(href, id) {
    return new Promise((resolve, reject) => {
        const existingLinkElement = document.getElementById(id);
        if (existingLinkElement) {
            document.head.removeChild(existingLinkElement);
        }

        const link = document.createElement('link');
        link.id = id; // Assign an id to find it later for removal
        link.rel = 'stylesheet';
        link.href = href;
        link.onload = () => resolve();
        link.onerror = () => reject(new Error('Stylesheet failed to load'));
        document.head.appendChild(link);
    });
}
// Function to load saved stylesheet
async function loadSavedStylesheet() {
    const savedStylesheet = getCookie('currentStylesheet');
    if (savedStylesheet) {
        try {
            await loadStylesheetAsync(savedStylesheet, 'themeStylesheet'); // 'themeStylesheet' is the id
            toggleEffectsBasedOnStylesheet(savedStylesheet);
        } catch (error) {
            console.error('Failed to load stylesheet:', error);
        }
    }
}


function changeStylesheet(newStylesheet) {
    // Modify to use new method
    loadStylesheetAsync(newStylesheet, 'themeStylesheet')
        .then(() => {
            // Save the stylesheet using cookie
            setCookie('currentStylesheet', newStylesheet, 365); // Save for 365 days
            toggleEffectsBasedOnStylesheet(newStylesheet);
        })
        .catch((error) => {
            console.error('Failed to load stylesheet:', error);
        });
}

function initializeThemeButtons() {
    const themeMapping = {
        'theme1': 'css/renaissancefinale.css',
        'theme2': 'css/be.css',
        'theme3': 'css/futurism.css',
        'theme4': 'css/pm.css',
        'theme5': 'css/XX.css',
        'theme6': 'css/2030.css'
    };

    Object.keys(themeMapping).forEach(theme => {
        document.querySelector(`.sub-btn[data-theme="${theme}"]`).addEventListener('click', function() {
            const newStylesheet = themeMapping[theme];
            changeStylesheet(newStylesheet);
            toggleEffectsBasedOnStylesheet(newStylesheet);
        });
    });
}

$(document).ready(async function() {
    // Load saved stylesheet
    await loadSavedStylesheet();

  function appendToMetadataList(className, listId, titleId) {
      var elements = $(className);
      var items = [];
      elements.each(function() {
          var name = $(this).text();
          var wikipediaUrl = $(this).data('wikipedia-url');
          items.push({ name: name, url: wikipediaUrl });
      });
      var uniqueItems = Array.from(new Set(items.map(i => i.name))).map(name => {
          return items.find(i => i.name === name);
      });
      if (uniqueItems.length > 0) {
          $(titleId).show();
      } else {
          $(titleId).hide();
      }
      var listHtml = uniqueItems.map(function(item) {
          if (item.url) {
              return `<li><a href="${item.url}" target="_blank">${item.name}</a></li>`;
          } else {
              return `<li>${item.name}</li>`;
          }
      }).join("");
      $(listId).append(listHtml);
  }

  $("#placeNames").change(function() {
      $("#placeNameList").empty();
      if (this.checked) {
          $(".placeName").addClass("highlight-place");
          appendToMetadataList(".highlight-place", "#placeNameList", "#placeNameTitle");
      } else {
          $(".placeName").removeClass("highlight-place");
          $("#placeNameTitle").hide();
      }
  });

  $("#personNames").change(function() {
      $("#personNameList").empty();
      if (this.checked) {
          $(".personName").addClass("highlight-person");
          appendToMetadataList(".highlight-person", "#personNameList", "#personNameTitle");
      } else {
          $(".personName").removeClass("highlight-person");
          $("#personNameTitle").hide();
      }
  });

});

let searchTerm = '';
let matchingElements = [];
let currentIndex = -1;

function performSearch() {
    searchTerm = $('#search-input').val().toLowerCase();
    clearHighlights();
    matchingElements = [];

    if (searchTerm) {
        const searchTermRegex = new RegExp('\\b' + searchTerm + '\\b', 'i'); // Utilizza una regex per trovare corrispondenze esatte della parola
        $('.personName, .placeName').each(function() {
            const text = $(this).text().toLowerCase();
            if (searchTermRegex.test(text)) {
                matchingElements.push(this);
            }
        });

        if (matchingElements.length > 0) {
            currentIndex = 0;
            clearHighlights();
            scrollCurrentOccurrenceIntoView();
            updateOccurrenceCount();
        } else {
            currentIndex = -1;
            clearHighlights();
            updateOccurrenceCount();
        }
    } else {
        currentIndex = -1;
        clearHighlights();
        updateOccurrenceCount();
    }
}

function clearHighlights() {
    $(matchingElements).removeClass('highlight');
}

function scrollCurrentOccurrenceIntoView() {
    if (currentIndex >= 0 && currentIndex < matchingElements.length) {
        const element = matchingElements[currentIndex];
        $(element).addClass('highlight');
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function updateOccurrenceCount() {
    $('#occurrences-count').text(`${currentIndex + 1} di ${matchingElements.length}`);
}

$('#search-input').on('input', performSearch);

$('#prev-button').on('click', function() {
    if (matchingElements.length > 0) {
        currentIndex = (currentIndex - 1 + matchingElements.length) % matchingElements.length;
        clearHighlights();
        scrollCurrentOccurrenceIntoView();
        updateOccurrenceCount();
    }
});

$('#next-button').on('click', function() {
    if (matchingElements.length > 0) {
        currentIndex = (currentIndex + 1) % matchingElements.length;
        clearHighlights();
        scrollCurrentOccurrenceIntoView();
        updateOccurrenceCount();
    }
});
/**/

document.getElementById('stylesBtn').addEventListener('click', function() {
    const themeButtons = document.querySelectorAll('.sub-btn[data-theme]');
    themeButtons.forEach(btn => {
        btn.style.display = (btn.style.display === 'none' || btn.style.display === '') ? 'block' : 'none';
    });
});

document.getElementById('toTopBtn').addEventListener('click', function() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
});

// Initialize theme buttons
initializeThemeButtons();


// effetto click futurismo 

function removeFuturismEffects() {
    const floatingWords = document.querySelectorAll('.floating-word');
    floatingWords.forEach(word => word.remove());
  }
  
  function isFuturismActive() {
    const currentStylesheet = document.getElementById('themeStylesheet').getAttribute('href');
    return currentStylesheet.includes('futurism.css');
  }
  
  function toggleEffectsBasedOnStylesheet() {
    if (isFuturismActive()) {
        activateFuturismEffects();
    } else {
        removeFuturismEffects();
    }
  }
  
  const wordText = "click";
  
  function createWord(className) {
      const word = document.createElement("div");
      word.textContent = wordText;
      word.classList.add('floating-word', className);
      document.body.appendChild(word);
  }
  
  function randomizeWordPosition(wordElement) {
      const randomTop = Math.random() * (window.innerHeight - 100);
      const randomLeft = Math.random() * (window.innerWidth - 100);
  
      wordElement.style.top = `${randomTop}px`;
      wordElement.style.left = `${randomLeft}px`;
  }
  
  function activateFuturismEffects() {
    for (let i = 1; i <= 7; i++) {
        const className = `word${i}`;
        createWord(className);
        const wordElement = document.querySelector(`.${className}`);
        randomizeWordPosition(wordElement);
    }
  }
  
  // Richiama la funzione quando la pagina viene caricata
  toggleEffectsBasedOnStylesheet();


//effetto titolo futurismo
const siteHeadingUpper = document.querySelector(".site-heading-upper");
            const text = siteHeadingUpper.textContent.trim();
            let newText = "";
            
            for (let letter of text) {
            if (letter === " ") {
            newText += letter; // non avvolgere gli spazi
            } else {
            newText += `<span class="overlap" data-overlap="${letter}">${letter}</span>`;
            }
            }
            
            siteHeadingUpper.innerHTML = newText;


            document.addEventListener('DOMContentLoaded', function() {
                const wrapLettersInSpans = (element) => {
                  const text = element.textContent.trim();
                  let wrappedText = "";
              
                  for (let letter of text) {
                    if (letter === " ") {
                      wrappedText += letter; // non avvolgere gli spazi
                    } else {
                      wrappedText += `<span>${letter}</span>`;
                    }
                  }
              
                  element.innerHTML = wrappedText;
                }
              
                const siteHeadingLower = document.querySelector(".site-heading-lower");
                
                if (siteHeadingLower) {
                  wrapLettersInSpans(siteHeadingLower);
                }
              });

              document.addEventListener('DOMContentLoaded', function() {
                const wrapAlternateLettersInSpans = (element) => {
                    const text = element.textContent.trim();
                    let wrappedText = "";
                    
                    for (let i = 0; i < text.length; i++) {
                        if (text[i] === " ") {
                            wrappedText += text[i]; // non avvolgere gli spazi
                        } else if (i % 2 === 0) { // avvolge solo le lettere in posizioni pari (0-based)
                            wrappedText += `<span>${text[i]}</span>`;
                        } else {
                            wrappedText += text[i];
                        }
                    }
                    
                    element.innerHTML = wrappedText;
                }
            
                // Applica l'effetto ai link della navbar nella visualizzazione normale
                const navLinks = document.querySelectorAll('#mainNav .nav-link');
                navLinks.forEach(navLink => {
                    wrapAlternateLettersInSpans(navLink);
                });
            
                // Applica l'effetto ai link della navbar nella visualizzazione contratta
                const collapsedNavLinks = document.querySelectorAll('#mainNav .navbar-collapse .nav-link');
                collapsedNavLinks.forEach(navLink => {
                    wrapAlternateLettersInSpans(navLink);
                });
            });


