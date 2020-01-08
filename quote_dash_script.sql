-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema quote_dash
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `quote_dash` ;

-- -----------------------------------------------------
-- Schema quote_dash
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `quote_dash` DEFAULT CHARACTER SET utf8 ;
USE `quote_dash` ;

-- -----------------------------------------------------
-- Table `quote_dash`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `quote_dash`.`users` ;

CREATE TABLE IF NOT EXISTS `quote_dash`.`users` (
  `id_users` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(255) NOT NULL,
  `last_name` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id_users`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `quote_dash`.`quotes`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `quote_dash`.`quotes` ;

CREATE TABLE IF NOT EXISTS `quote_dash`.`quotes` (
  `id_quotes` INT NOT NULL AUTO_INCREMENT,
  `content` LONGTEXT NOT NULL,
  `author` INT NOT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  `author_name` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id_quotes`),
  INDEX `fk_quotes_users_idx` (`author` ASC) VISIBLE,
  CONSTRAINT `fk_quotes_users`
    FOREIGN KEY (`author`)
    REFERENCES `quote_dash`.`users` (`id_users`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `quote_dash`.`liked_quotes`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `quote_dash`.`liked_quotes` ;

CREATE TABLE IF NOT EXISTS `quote_dash`.`liked_quotes` (
  `users_id_users` INT NOT NULL,
  `quotes_id_quotes` INT NOT NULL,
  PRIMARY KEY (`users_id_users`, `quotes_id_quotes`),
  INDEX `fk_users_has_quotes_quotes1_idx` (`quotes_id_quotes` ASC) VISIBLE,
  INDEX `fk_users_has_quotes_users1_idx` (`users_id_users` ASC) VISIBLE,
  CONSTRAINT `fk_users_has_quotes_users1`
    FOREIGN KEY (`users_id_users`)
    REFERENCES `quote_dash`.`users` (`id_users`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_has_quotes_quotes1`
    FOREIGN KEY (`quotes_id_quotes`)
    REFERENCES `quote_dash`.`quotes` (`id_quotes`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
