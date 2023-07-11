CREATE TABLE IF NOT EXISTS Users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	discordId INTEGER NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Cups (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	cupName text NOT NULL UNIQUE,
    cupEmojiName text NOT NULL UNIQUE,
    cupEmojiId INTEGER NOT NULL UNIQUE,
    cupUrl text NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Tracks (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	trackName text NOT NULL UNIQUE,
    cupId INTEGER NOT NULL,
    trackUrl text,
    FOREIGN KEY (cupId) REFERENCES Cups (id)
);

CREATE TABLE IF NOT EXISTS Servers (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	serverId INTEGER NOT NULL,
    discordId INTEGER NOT NULL,
    FOREIGN KEY (discordId) REFERENCES Users (discordId),
    UNIQUE(serverId, discordId)
);

CREATE TABLE IF NOT EXISTS Ni150 (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	discordId INTEGER NOT NULL,
    trackName text NOT NULL,
    time text NOT NULL,
    link text,
    FOREIGN KEY (discordId) REFERENCES Users (discordId),
    FOREIGN KEY (trackName) REFERENCES Users (trackName),
    UNIQUE(discordId, trackName)
);

CREATE TABLE IF NOT EXISTS Sh150 (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	discordId INTEGER NOT NULL,
    trackName text NOT NULL,
    time text NOT NULL,
    link text,
    FOREIGN KEY (discordId) REFERENCES Users (discordId),
    FOREIGN KEY (trackName) REFERENCES Users (trackName),
    UNIQUE(discordId, trackName)
);

CREATE TABLE IF NOT EXISTS Ni200 (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	discordId INTEGER NOT NULL,
    trackName text NOT NULL,
    time text NOT NULL,
    link text,
    FOREIGN KEY (discordId) REFERENCES Users (discordId),
    FOREIGN KEY (trackName) REFERENCES Users (trackName),
    UNIQUE(discordId, trackName)
);

CREATE TABLE IF NOT EXISTS Sh200 (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	discordId INTEGER NOT NULL,
    trackName text NOT NULL,
    time text NOT NULL,
    link text,
    FOREIGN KEY (discordId) REFERENCES Users (discordId),
    FOREIGN KEY (trackName) REFERENCES Users (trackName),
    UNIQUE(discordId, trackName)
);