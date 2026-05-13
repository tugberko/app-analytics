DROP TABLE IF EXISTS platforms;
CREATE TABLE platforms (
    id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(10) NOT NULL
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
