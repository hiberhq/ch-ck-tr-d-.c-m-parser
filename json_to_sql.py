#!/usr/bin/env python3

import os
import json

intro = '''
SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- База данных: `checkatrade`
--

-- --------------------------------------------------------

--
-- Структура таблицы `companies`
--

CREATE DATABASE IF NOT EXISTS companies;
USE companies;

CREATE TABLE IF NOT EXISTS `companies` (
	`name` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
	`pageURL` varchar(312) COLLATE utf8mb4_unicode_ci NOT NULL,
	`contact` varchar(96) COLLATE utf8mb4_unicode_ci NOT NULL,
	`phones` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
	`email` varchar(96) COLLATE utf8mb4_unicode_ci NOT NULL,
	`website` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
	`score` varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL,
	`reliability` varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL,
	`tidiness` varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL,
	`courtesy` varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL,
	`workmanship` varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL,
	`reviews` varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL,
	`basedIn` varchar(312) COLLATE utf8mb4_unicode_ci NOT NULL,
	`worksIn` varchar(312) COLLATE utf8mb4_unicode_ci NOT NULL,
	`postcode` varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL,
	`category` varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL,
	`categoryName` varchar(96) COLLATE utf8mb4_unicode_ci NOT NULL,
	`gasSafeNumber` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
	`companyType` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
	`companyOwner` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
	`companyLimitedCheked` varchar(312) COLLATE utf8mb4_unicode_ci NOT NULL,
	`companyVAT` varchar(312) COLLATE utf8mb4_unicode_ci NOT NULL,
	`publicLiabilityInsurance` varchar(312) COLLATE utf8mb4_unicode_ci NOT NULL,
	`insuredBy` varchar(312) COLLATE utf8mb4_unicode_ci NOT NULL,
	`insuranceAmount` varchar(312) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Дамп данных таблицы `companies`
--
'''

insert = 'INSERT INTO `companies` (`name`, `pageURL`, `contact`, `phones`, `email`, `website`, `score`, `reliability`, `tidiness`, `courtesy`, `workmanship`, `reviews`, `basedIn`, `worksIn`, `postcode`, `category`, `categoryName`, `gasSafeNumber`, `companyType`, `companyOwner`, `companyLimitedCheked`, `companyVAT`, `publicLiabilityInsurance`, `insuredBy`, `insuranceAmount`) VALUES'

try:
	with open('data.json', 'r') as file:
		data = json.loads(file.read())
	
	i = 0
	out = intro + '\n'
	for item in data:
		# Skip bad values
		if item == None:
			print('Bad value index is %s' % i)
			continue
			
		if i % 200 == 0 or i == 0:
			out += ';\n' + insert if i != 0 else '\n' + insert + '\n'
		else:
			out += ',\n'
			
		out += '('
		
		n = 0
		for key, value in item.items():
			sep = '' if n == len(item) - 1 else ', '
			out += '\'' + value.replace("'", "\\'") + '\'' + sep
			n += 1
		out += ');' if i == len(data) - 1 else ')'
			
		i += 1

	try:
		with open('data.sql', 'w') as file:
			file.write(out)
		print('...DONE!')
	except OSError as e:
		print('Cannot write in file %s. %s' % ('data.sql', e))
	
except OSError as e:
	print('Cannot open file %s. %s' % ('data.json', e))

