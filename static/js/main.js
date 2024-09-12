document.addEventListener('DOMContentLoaded', () => {
    const conceptInput = document.getElementById('concept-input');
    const generateBtn = document.getElementById('generate-btn');
    const resultsDiv = document.getElementById('results');
    const loadingDiv = document.querySelector('.loading');

    function generateHypothesis() {
        const text = conceptInput.value;
        
        if (text.trim().length < 10) {
            alert('Please enter a more detailed text (at least 10 characters).');
            return;
        }

        // Show loading indicator
        loadingDiv.style.display = 'block';
        generateBtn.disabled = true;
        resultsDiv.innerHTML = '';

        fetch('/generate_hypothesis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
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
                                    updateResults(data);
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
        })
        .finally(() => {
            // Hide loading indicator
            loadingDiv.style.display = 'none';
            generateBtn.disabled = false;
        });
    }

    function updateResults(data) {
        let sectionId = `${data.stage}-result`;
        let sectionElement = document.getElementById(sectionId);

        if (!sectionElement) {
            resultsDiv.innerHTML += `
                <div class="result-section">
                    <h2>${capitalizeFirstLetter(data.stage)} ${data.stage === 'scientist' ? 'Hypothesis' : 'Analysis'}</h2>
                    <div id="${sectionId}"></div>
                </div>
            `;
            sectionElement = document.getElementById(sectionId);
        }

        if (data.stage === 'graph_analysis') {
            const graphAnalysis = JSON.parse(data.content);
            sectionElement.innerHTML = formatGraphAnalysis(graphAnalysis);
        } else if (data.stage === 'concept_extraction') {
            sectionElement.innerHTML = `<p>Extracted concepts: ${data.content}</p>`;
        } else {
            sectionElement.innerHTML += formatContent(data.content);
        }
    }

    function formatGraphAnalysis(analysis) {
        let html = '<h3>Graph Analysis Results</h3>';
        
        // PageRank
        html += '<h4>Top 5 Nodes by PageRank</h4>';
        html += '<ul>';
        Object.entries(analysis.centrality.pagerank)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .forEach(([node, score]) => {
                html += `<li>${node}: ${score.toFixed(3)}</li>`;
            });
        html += '</ul>';

        // Communities
        html += '<h4>Communities</h4>';
        html += `<p>Number of communities detected: ${analysis.communities.length}</p>`;

        // Clusters
        html += '<h4>Clusters</h4>';
        html += `<p>Number of clusters: ${new Set(Object.values(analysis.clusters)).size}</p>`;

        // Link Predictions
        html += '<h4>Top 3 Predicted Links</h4>';
        html += '<ul>';
        analysis.link_predictions.slice(0, 3).forEach(([u, v, score]) => {
            html += `<li>(${u}, ${v}) - Score: ${score.toFixed(3)}</li>`;
        });
        html += '</ul>';

        return html;
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

    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
});
