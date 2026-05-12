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

DROP TABLE IF EXISTS app_installs;
CREATE TABLE app_installs (
    id INT NOT NULL AUTO_INCREMENT,
    install_uuid CHAR(36) NOT NULL,
    platform_id TINYINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_install_uuid (install_uuid)
);

DROP TABLE IF EXISTS heartbeats;
CREATE TABLE heartbeats (
    id INT NOT NULL AUTO_INCREMENT,
    app_install_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at_local DATETIME NOT NULL,
    

    PRIMARY KEY (id),

    INDEX idx_app_install_id (app_install_id),

    CONSTRAINT fk_heartbeats_app_installs
        FOREIGN KEY (app_install_id)
        REFERENCES app_installs (id)
        ON DELETE CASCADE
);