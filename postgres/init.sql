-- Tabulka měn
CREATE TABLE currencies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(3) NOT NULL UNIQUE  -- Např. 'EUR', 'USD', 'CZK'
);

-- Tabulka směnných kurzů
CREATE TABLE exchange_rates (
    id SERIAL PRIMARY KEY,
    base_currency_id INT NOT NULL,
    target_currency_id INT NOT NULL,
    rate FLOAT NOT NULL,
    FOREIGN KEY (base_currency_id) REFERENCES currencies(id),
    FOREIGN KEY (target_currency_id) REFERENCES currencies(id)
);

INSERT INTO currencies (name) VALUES 
('EUR'), ('AED'), ('AFN'), ('ALL'), ('AMD'), ('ANG'), ('AOA'), ('ARS'), ('AUD'),
('AWG'), ('AZN'), ('BAM'), ('BBD'), ('BDT'), ('BGN'), ('BHD'), ('BIF'), ('BMD'),
('BND'), ('BOB'), ('BRL'), ('BSD'), ('BTN'), ('BWP'), ('BYN'), ('BZD'), ('CAD'),
('CDF'), ('CHF'), ('CLP'), ('CNY'), ('COP'), ('CRC'), ('CUP'), ('CVE'), ('CZK'),
('DJF'), ('DKK'), ('DOP'), ('DZD'), ('EGP'), ('ERN'), ('ETB'), ('FJD'), ('FKP'),
('FOK'), ('GBP'), ('GEL'), ('GGP'), ('GHS'), ('GIP'), ('GMD'), ('GNF'), ('GTQ'),
('GYD'), ('HKD'), ('HNL'), ('HRK'), ('HTG'), ('HUF'), ('IDR'), ('ILS'), ('IMP'),
('INR'), ('IQD'), ('IRR'), ('ISK'), ('JEP'), ('JMD'), ('JOD'), ('JPY'), ('KES'),
('KGS'), ('KHR'), ('KID'), ('KMF'), ('KRW'), ('KWD'), ('KYD'), ('KZT'), ('LAK'),
('LBP'), ('LKR'), ('LRD'), ('LSL'), ('LYD'), ('MAD'), ('MDL'), ('MGA'), ('MKD'),
('MMK'), ('MNT'), ('MOP'), ('MRU'), ('MUR'), ('MVR'), ('MWK'), ('MXN'), ('MYR'),
('MZN'), ('NAD'), ('NGN'), ('NIO'), ('NOK'), ('NPR'), ('NZD'), ('OMR'), ('PAB'),
('PEN'), ('PGK'), ('PHP'), ('PKR'), ('PLN'), ('PYG'), ('QAR'), ('RON'), ('RSD'),
('RUB'), ('RWF'), ('SAR'), ('SBD'), ('SCR'), ('SDG'), ('SEK'), ('SGD'), ('SHP'),
('SLE'), ('SLL'), ('SOS'), ('SRD'), ('SSP'), ('STN'), ('SYP'), ('SZL'), ('THB'),
('TJS'), ('TMT'), ('TND'), ('TOP'), ('TRY'), ('TTD'), ('TVD'), ('TWD'), ('TZS'),
('UAH'), ('UGX'), ('USD'), ('UYU'), ('UZS'), ('VES'), ('VND'), ('VUV'), ('WST'),
('XAF'), ('XCD'), ('XCG'), ('XDR'), ('XOF'), ('XPF'), ('YER'), ('ZAR'), ('ZMW'),
('ZWL');