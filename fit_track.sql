CREATE DATABASE fitness_tracker;

USE fitness_tracker;

CREATE TABLE Members(
	id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(12),
    credit_card VARCHAR(30)
);

CREATE TABLE Workouts (
	id INT AUTO_INCREMENT PRIMARY KEY,
    activity VARCHAR(255) NOT NULL,
    date DATE, -- "yyyy-mm-dd"
    member_id INT NOT NULL,
    FOREIGN KEY(member_id) REFERENCES Members(id)
);

