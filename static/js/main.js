document.addEventListener('DOMContentLoaded', () => {
    const conceptInput = document.getElementById('concept-input');
    const generateBtn = document.getElementById('generate-btn');
    const resultsDiv = document.getElementById('results');

    function generateHypothesis() {
        const concepts = conceptInput.value.split(',').map(c => c.trim());
        
        if (concepts.length < 2) {
            alert('Please enter at least two concepts separated by commas.');
            return;
        }

        resultsDiv.innerHTML = `
            <div class="result-section">
                <h2>Ontologist Analysis</h2>
                <div id="ontologist-result"></div>
            </div>
            <div class="result-section">
                <h2>Scientist Hypothesis</h2>
                <div id="scientist-result"></div>
            </div>
            <div class="result-section">
                <h2>Critic Review</h2>
                <div id="critic-result"></div>
            </div>
        `;

        const ontologistResult = document.getElementById('ontologist-result');
        const scientistResult = document.getElementById('scientist-result');
        const criticResult = document.getElementById('critic-result');

        fetch('/generate_hypothesis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ concepts })
        })
        .then(response => {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            return new ReadableStream({
                start(controller) {
                    function push() {
                        reader.read().then(({ done, value }) => {
                            if (done) {
                                controller.close();
                                return;
                            }

                            const decodedChunk = decoder.decode(value);
                            const events = decodedChunk.split('\n\n');

                            for (const event of events) {
                                if (event.startsWith('data: ')) {
                                    const data = JSON.parse(event.slice(6));
                                    switch (data.stage) {
                                        case 'ontologist':
                                            ontologistResult.innerHTML += formatContent(data.content);
                                            break;
                                        case 'scientist':
                                            scientistResult.innerHTML += formatContent(data.content);
                                            break;
                                        case 'critic':
                                            criticResult.innerHTML += formatContent(data.content);
                                            break;
                                    }
                                }
                            }

                            push();
                        });
                    }

                    push();
                }
            });
        })
        .catch(error => {
            console.error('Error:', error);
            resultsDiv.innerHTML = '<p>An error occurred while generating the hypothesis.</p>';
        });
    }

    generateBtn.addEventListener('click', generateHypothesis);

    // Add event listener for Enter key press
    conceptInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            generateHypothesis();
        }
    });

    function formatContent(content) {
        // Split content into paragraphs
        const paragraphs = content.split('\n\n');
        
        // Process each paragraph
        const formattedParagraphs = paragraphs.map(paragraph => {
            // Check if the paragraph is a list
            if (paragraph.includes('\n- ')) {
                const listItems = paragraph.split('\n- ');
                const listHeader = listItems.shift();
                return `<p>${listHeader}</p><ul>${listItems.map(item => `<li>${item.trim()}</li>`).join('')}</ul>`;
            } else {
                return `<p>${paragraph}</p>`;
            }
        });

        return formattedParagraphs.join('');
    }
});
