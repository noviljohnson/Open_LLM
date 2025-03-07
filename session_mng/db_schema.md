-- Enable the pgcrypto extension for UUID generation
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Create the 'users' table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(), -- Unique identifier for the user
    user_ip INET UNIQUE NOT NULL,                      -- User's IP address (unique)
    user_name VARCHAR(255) NOT NULL                    -- User's name (cannot be null)
);

-- 2. Create the 'chat_sessions' table
CREATE TABLE chat_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(), -- Unique identifier for the session
    user_id UUID NOT NULL,                                -- Foreign key to the 'users' table
    session_name VARCHAR(255) NOT NULL,                   -- Name of the chat session (cannot be null)
    app_name VARCHAR(100) NOT NULL,                       -- Name of the application (cannot be null)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Timestamp when the session was created
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE -- Foreign key constraint
);

-- 3. Create the 'chat_history' table
CREATE TABLE chat_history (
    history_id SERIAL PRIMARY KEY,                       -- Auto-incrementing unique ID for each message
    user_id UUID NOT NULL,                               -- Foreign key to the 'users' table
    session_id UUID NOT NULL,                            -- Foreign key to the 'chat_sessions' table
    app_name VARCHAR(100) NOT NULL,                      -- Name of the application (cannot be null)
    message TEXT,                                        -- The chat message (can be null)
    sender VARCHAR(255),                                 -- Sender of the message (can be null)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Timestamp when the message was created
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE, -- Foreign key to 'users'
    CONSTRAINT fk_session FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE -- Foreign key to 'chat_sessions'
);
