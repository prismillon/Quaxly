-- Drop existing foreign key constraints
DROP INDEX IF EXISTS idx_ni150_track;
DROP INDEX IF EXISTS idx_sh150_track;
DROP INDEX IF EXISTS idx_ni200_track;
DROP INDEX IF EXISTS idx_sh200_track;

-- Create temporary tables with the desired schema
CREATE TABLE Ni150_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discordId INTEGER NOT NULL,
    trackName text NOT NULL,
    time text NOT NULL,
    link text,
    FOREIGN KEY (discordId) REFERENCES Users (discordId),
    FOREIGN KEY (trackName) REFERENCES Tracks (trackName),
    UNIQUE(discordId, trackName)
);

CREATE TABLE Sh150_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discordId INTEGER NOT NULL,
    trackName text NOT NULL,
    time text NOT NULL,
    link text,
    FOREIGN KEY (discordId) REFERENCES Users (discordId),
    FOREIGN KEY (trackName) REFERENCES Tracks (trackName),
    UNIQUE(discordId, trackName)
);

CREATE TABLE Ni200_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discordId INTEGER NOT NULL,
    trackName text NOT NULL,
    time text NOT NULL,
    link text,
    FOREIGN KEY (discordId) REFERENCES Users (discordId),
    FOREIGN KEY (trackName) REFERENCES Tracks (trackName),
    UNIQUE(discordId, trackName)
);

CREATE TABLE Sh200_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discordId INTEGER NOT NULL,
    trackName text NOT NULL,
    time text NOT NULL,
    link text,
    FOREIGN KEY (discordId) REFERENCES Users (discordId),
    FOREIGN KEY (trackName) REFERENCES Tracks (trackName),
    UNIQUE(discordId, trackName)
);

-- Copy data from the original tables to the temporary tables
INSERT INTO Ni150_temp (discordId, trackName, time, link)
SELECT discordId, trackName, time, link FROM Ni150;

INSERT INTO Sh150_temp (discordId, trackName, time, link)
SELECT discordId, trackName, time, link FROM Sh150;

INSERT INTO Ni200_temp (discordId, trackName, time, link)
SELECT discordId, trackName, time, link FROM Ni200;

INSERT INTO Sh200_temp (discordId, trackName, time, link)
SELECT discordId, trackName, time, link FROM Sh200;

-- Drop the original tables
DROP TABLE Ni150;
DROP TABLE Sh150;
DROP TABLE Ni200;
DROP TABLE Sh200;

-- Rename the temporary tables to the original table names
ALTER TABLE Ni150_temp RENAME TO Ni150;
ALTER TABLE Sh150_temp RENAME TO Sh150;
ALTER TABLE Ni200_temp RENAME TO Ni200;
ALTER TABLE Sh200_temp RENAME TO Sh200;
