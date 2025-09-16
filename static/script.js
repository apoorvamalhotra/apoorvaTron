let userId = null;
let extractedData = null;

document.addEventListener('DOMContentLoaded', function() {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const startChatBtn = document.getElementById('start-chat-btn');
    const sessionPopup = document.getElementById('session-popup');
    const chatContainer = document.getElementById('chat-container');
    const seeExtractionBtn = document.getElementById('see-extraction-btn');
    const extractionPopup = document.getElementById('extraction-popup');
    const closeExtractionBtn = document.getElementById('close-extraction-btn');
    const copyExtractionBtn = document.getElementById('copy-extraction-btn');

    // Add event listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    startChatBtn.addEventListener('click', function() {
        startChat();
    });


    seeExtractionBtn.addEventListener('click', function() {
        showExtractionPopup();
    });

    closeExtractionBtn.addEventListener('click', function() {
        hideExtractionPopup();
    });

    copyExtractionBtn.addEventListener('click', function() {
        copyExtractionToClipboard();
    });


    // Show popup on load
    showSessionPopup();
});

function showSessionPopup() {
    document.getElementById('session-popup').classList.remove('hidden');
    document.getElementById('chat-container').classList.add('hidden');
}

function hideSessionPopup() {
    document.getElementById('session-popup').classList.add('hidden');
    document.getElementById('chat-container').classList.remove('hidden');
}

function startChat() {
    // Generate a random test ID automatically
    const testId = 'test_' + Math.random().toString(36).substr(2, 9);
    userId = testId;
    extractedData = null;
    hideSessionPopup();
    clearChatBox();
    hideExtractionButton();
    
    // Reset input state
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    if (userInput) {
        userInput.disabled = false;
        userInput.placeholder = 'Type your message...';
        userInput.value = '';
    }
    if (sendButton) {
        sendButton.disabled = false;
    }
    
    sendHiMessage();
}

function clearChatBox() {
    document.getElementById('chat-box').innerHTML = '';
}

function updateSessionDisplay() {
    if (userId) {
        // Session display removed - now using switch session button
    } else {
        // Session display removed - now using switch session button
    }
}

function showExtractionPopup() {
    if (extractedData) {
        document.getElementById('extraction-json').textContent = JSON.stringify(extractedData, null, 2);
        document.getElementById('extraction-popup').classList.remove('hidden');
    }
}

function hideExtractionPopup() {
    document.getElementById('extraction-popup').classList.add('hidden');
}

function hideExtractionButton() {
    document.getElementById('see-extraction-btn').classList.add('hidden');
}

function copyExtractionToClipboard() {
    if (extractedData) {
        const jsonString = JSON.stringify(extractedData, null, 2);
        navigator.clipboard.writeText(jsonString).then(function() {
            // Show a brief success message
            const copyBtn = document.getElementById('copy-extraction-btn');
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            copyBtn.style.background = '#28a745';
            
            setTimeout(function() {
                copyBtn.textContent = originalText;
                copyBtn.style.background = '#6c757d';
            }, 2000);
        }).catch(function(err) {
            console.error('Failed to copy: ', err);
            alert('Failed to copy to clipboard');
        });
    }
}

async function sendHiMessage() {
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_input: "hi",
                userid: userId
            })
        });

        const data = await response.json();
        
        if (data.error) {
            addMessage(data.error, 'bot');
            return;
        }
        
        if (data.userid) {
            userId = data.userid;
            updateSessionDisplay();
        }
        
        if (data.next_question) {
            addMessage(data.next_question, 'bot');
        }
    } catch (error) {
        console.error('Error sending hi message:', error);
        addMessage('Sorry, there was an error starting the conversation. Please refresh the page.', 'bot');
    }
}

async function sendMessage() {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const message = userInput.value.trim();

    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');
    userInput.value = '';
    
    // Disable input while processing
    userInput.disabled = true;
    sendButton.disabled = true;
    
    // Show typing indicator
    showTypingIndicator();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_input: message,
                userid: userId
            })
        });

        const data = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        if (data.error) {
            addMessage(data.error, 'bot');
            return;
        }
        
        if (data.userid) {
            userId = data.userid;
            updateSessionDisplay();
        }
        
        if (data.next_question) {
            addMessage(data.next_question, 'bot');
        }
        
        // Check if there's an error or completion
        if (data.status === 'error') {
            userInput.disabled = false;
            sendButton.disabled = false;
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();
        addMessage('Sorry, there was an error processing your message. Please try again.', 'bot');
    } finally {
        // Re-enable input
        userInput.disabled = false;
        sendButton.disabled = false;
        userInput.focus();
    }
}

function addMessage(text, sender) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.textContent = text;
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showTypingIndicator() {
    const chatBox = document.getElementById('chat-box');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = '<div class="typing-dots"></div>';
    
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Switch session functionality
document.addEventListener('DOMContentLoaded', function() {
    const switchSessionBtn = document.getElementById('switch-session-btn');
    
    if (switchSessionBtn) {
        switchSessionBtn.addEventListener('click', function() {
            // Hide chat container
            const chatContainer = document.getElementById('chat-container');
            if (chatContainer) {
                chatContainer.classList.add('hidden');
            }
            
            // Show session popup
            const sessionPopup = document.getElementById('session-popup');
            if (sessionPopup) {
                sessionPopup.classList.remove('hidden');
            }
            
            
            // Clear chat history
            const chatBox = document.getElementById('chat-box');
            if (chatBox) {
                chatBox.innerHTML = '';
            }
            
            // Reset input state
            const userInput = document.getElementById('user-input');
            const sendButton = document.getElementById('send-button');
            if (userInput) {
                userInput.disabled = false;
                userInput.placeholder = 'Type your message...';
                userInput.value = '';
            }
            if (sendButton) {
                sendButton.disabled = false;
            }
            
            // Hide extraction button
            const seeExtractionBtn = document.getElementById('see-extraction-btn');
            if (seeExtractionBtn) {
                seeExtractionBtn.classList.add('hidden');
            }
        });
    }
});
