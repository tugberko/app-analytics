DROP TABLE IF EXISTS platforms;
CREATE TABLE platforms (
    id TINYINT UNSIGNED NOT NULL PRIMARY KEY,
    name VARCHAR(10) NOT NULL
);
INSERT INTO platforms (id, name) VALUES
(0, 'iOS'),
(1, 'Android'),
(2, 'Other');

DROP TABLE  IF EXISTS versions;
CREATE TABLE versions (
    id SMALLINT UNSIGNED NOT NULL PRIMARY KEY,
    version VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO versions (id, version) VALUES
(0, '1.0.0');

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
