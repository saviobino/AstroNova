CREATE DATABASE `baby_names` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;


CREATE TABLE `details` (
  `dataid` int NOT NULL,
  `name_details` json DEFAULT NULL,
  `names_with_similar_meanings` json DEFAULT NULL,
  `numerology_details` json DEFAULT NULL,
  `astrology_details` json DEFAULT NULL,
  `personality_details` json DEFAULT NULL,
  PRIMARY KEY (`dataid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `names` (
  `name` varchar(100) NOT NULL,
  `meaning` text,
  `gender` varchar(20) DEFAULT NULL,
  `religion` varchar(50) DEFAULT NULL,
  `dataid` int NOT NULL,
  UNIQUE KEY `name` (`name`),
  KEY `idx_names_dataid` (`dataid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `masterdata` (
  `dataid` INT NOT NULL,                               -- Foreign key from details and names tables
  `name` VARCHAR(100) NOT NULL,                       -- From names table
  `meaning` TEXT,                                     -- From names table
  `gender` VARCHAR(20) DEFAULT NULL,                  -- From names table
  `religion` VARCHAR(50) DEFAULT NULL,                -- From names table
  `name_details` JSON DEFAULT NULL,                   -- From details table
  `names_with_similar_meanings` JSON DEFAULT NULL,    -- From details table
  `numerology_details` JSON DEFAULT NULL,             -- From details table
  `astrology_details` JSON DEFAULT NULL,              -- From details table
  `personality_details` JSON DEFAULT NULL,            -- From details table
  PRIMARY KEY (`dataid`),                             -- Ensures unique entries by dataid
  FOREIGN KEY (`dataid`) REFERENCES `details` (`dataid`) ON DELETE CASCADE, -- Reference to details
  FOREIGN KEY (`dataid`) REFERENCES `names` (`dataid`) ON DELETE CASCADE    -- Reference to names
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

