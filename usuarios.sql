DROP TABLE IF EXISTS USUARIOS;

CREATE TABLE USUARIOS 
(
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	NOME  VARCHAR(100) NOT NULL,
    EMAIL VARCHAR(100) UNIQUE NOT NULL,
	SENHA VARCHAR(255) NOT NULL,
	PAPEL VARCHAR(20) NOT NULL CHECK (PAPEL IN ('Cliente', 'Funcionario', 'Dono'))
);

-- Senha padrão para todos os logins mockados: 123 (SHA-256)
INSERT INTO USUARIOS (NOME, EMAIL, SENHA, PAPEL) VALUES
	('Carlos Dono', 'dono@barbearia.com', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'Dono'),
	('João Barbeiro', 'joao@barbearia.com', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'Funcionario'),
	('Pedro Barbeiro', 'pedro@barbearia.com', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'Funcionario'),
	('Maria Cabeleireira', 'maria@barbearia.com', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'Funcionario'),
	('Ana Cabeleireira', 'ana@barbearia.com', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'Funcionario');