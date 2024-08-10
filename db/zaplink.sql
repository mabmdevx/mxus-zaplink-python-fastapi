-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 31, 2024 at 02:59 AM
-- Server version: 10.4.25-MariaDB
-- PHP Version: 8.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `zaplink`
--
CREATE DATABASE IF NOT EXISTS `zaplink` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `zaplink`;

-- --------------------------------------------------------

--
-- Table structure for table `urls`
--

CREATE TABLE `urls` (
  `urlx_id` bigint(20) NOT NULL,
  `urlx_original_url` varchar(255) NOT NULL,
  `urlx_hash` varchar(255) NOT NULL,
  `urlx_slug` varchar(20) NOT NULL,
  `urlx_is_safe` tinyint(1) NOT NULL DEFAULT 0,
  `urlx_unsafe_details` text NOT NULL,
  `urlx_visit_count` int(11) NOT NULL DEFAULT 0,
  `created_on` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_on` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `urls`
--

INSERT INTO `urls` (`urlx_id`, `urlx_original_url`, `urlx_hash`, `urlx_slug`, `urlx_is_safe`, urlx_visit_count`, `created_on`, `updated_on`) VALUES
(1, 'https://google.com', '05046f26c83e8c88b3ddab2eab63d0d16224ac1e564535fc75cdceee47a0938d', 'imhkFZPB', 1, 1, '2024-07-28 20:48:02', '2024-07-29 16:54:03'),
(2, 'https://yahoo.com', 'cf0d7b5c6127539ad60bd842602cff8f8009ca3b5158acdb57091f7e6218ee22', '5UJcv9U9', 1, 2, '2024-07-29 08:58:30', '2024-07-29 16:06:46');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `urls`
--
ALTER TABLE `urls`
  ADD PRIMARY KEY (`urlx_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `urls`
--
ALTER TABLE `urls`
  MODIFY `urlx_id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
