DROP TABLE IF EXISTS refresh_tokens;
CREATE TABLE refresh_tokens (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    token_hash CHAR(64) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    revoked_at DATETIME NULL,

    INDEX idx_user_id (user_id),
    INDEX idx_token_hash (token_hash)
);




DROP TABLE IF EXISTS email_otps;
CREATE TABLE email_otps (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,

    email VARCHAR(255) NOT NULL,

    otp_hash VARCHAR(255) NOT NULL,

    expires_at TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL 5 MINUTE),

    attempts INT NOT NULL DEFAULT 0,

    max_attempts INT NOT NULL DEFAULT 5,

    is_used BOOL NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_email (email),
    INDEX idx_expires_at (expires_at)
);

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS platforms;
CREATE TABLE platforms (
    id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(10) NOT NULL UNIQUE
);


DROP TABLE  IF EXISTS versions;
CREATE TABLE versions (
    id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    version VARCHAR(20) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);



DROP TABLE IF EXISTS app_installations;
CREATE TABLE app_installations (
    id INT NOT NULL AUTO_INCREMENT,
    install_uuid CHAR(36) NOT NULL,
    platform_id TINYINT NOT NULL,
    locale_id TINYINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_install_uuid (install_uuid)
);

DROP TABLE IF EXISTS heartbeats;
CREATE TABLE heartbeats (
    id INT NOT NULL AUTO_INCREMENT,
    app_installation_id INT NOT NULL,
    version_id SMALLINT NOT NULL,
    time_since_last_startup_s INT NOT NULL,
    created_at_local DATETIME NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    INDEX idx_app_installation_id (app_installation_id)
);

DROP TABLE IF EXISTS locales;
CREATE TABLE locales (
    id INT NOT NULL AUTO_INCREMENT,
    locale VARCHAR(32) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY unique_locale (locale)
);


GRANT DELETE ON app_analytics_db.email_otps TO 'fastapi_app'@'localhost';