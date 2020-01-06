-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema computer_lab_log
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema computer_lab_log
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `computer_lab_log` DEFAULT CHARACTER SET utf8 ;
USE `computer_lab_log` ;

-- -----------------------------------------------------
-- Table `computer_lab_log`.`purposes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `computer_lab_log`.`purposes` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `purpose_name` VARCHAR(45) NOT NULL,
  `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 8
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `computer_lab_log`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `computer_lab_log`.`users` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(45) NOT NULL,
  `last_name` VARCHAR(45) NOT NULL,
  `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idx_name_phone` (`first_name` ASC, `last_name` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 28
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `computer_lab_log`.`timeclocks`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `computer_lab_log`.`timeclocks` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `timein` DATETIME NULL DEFAULT NULL,
  `timeout` DATETIME NULL DEFAULT NULL,
  `span` INT(11) NULL DEFAULT NULL,
  `users_id` INT(11) NOT NULL,
  `purposes_id` INT(11) NOT NULL,
  `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `unique_timestamp` (`timein` ASC, `users_id` ASC) VISIBLE,
  INDEX `fk_timeclocks_users_idx` (`users_id` ASC) VISIBLE,
  INDEX `fk_timeclocks_purposes1_idx` (`purposes_id` ASC) VISIBLE,
  CONSTRAINT `fk_timeclocks_purposes1`
    FOREIGN KEY (`purposes_id`)
    REFERENCES `computer_lab_log`.`purposes` (`id`),
  CONSTRAINT `fk_timeclocks_users`
    FOREIGN KEY (`users_id`)
    REFERENCES `computer_lab_log`.`users` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 157
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
