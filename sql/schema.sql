-- sql/schema.sql

CREATE SCHEMA IF NOT EXISTS "sql-cblab";
SET search_path TO "sql-cblab";

CREATE TABLE IF NOT EXISTS "ErpMetadata" (
    "curUTC" TIMESTAMP PRIMARY KEY,
    "locRef" VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS "employee" (
    "empNum" INT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS "guestChecks" (
    "guestCheckId" BIGINT PRIMARY KEY,
    "chkNum" INT,
    "opnBusDt" DATE,
    "opnUTC" TIMESTAMP,
    "opnLcl" TIMESTAMP,
    "clsdBusDt" DATE,
    "clsdUTC" TIMESTAMP,
    "clsdLcl" TIMESTAMP,
    "lastTransUTC" TIMESTAMP,
    "lastTransLcl" TIMESTAMP,
    "lastUpdatedUTC" TIMESTAMP,
    "lastUpdatedLcl" TIMESTAMP,
    "clsdFlag" BOOLEAN,
    "gstCnt" INT,
    "subTtl" NUMERIC(10,2),
    "nonTxblSlsTtl" NUMERIC(10,2),
    "chkTtl" NUMERIC(10,2),
    "dscTtl" NUMERIC(10,2),
    "payTtl" NUMERIC(10,2),
    "balDueTtl" NUMERIC(10,2),
    "rvcNum" INT,
    "otNum" INT,
    "ocNum" INT,
    "tblNum" INT,
    "tblName" VARCHAR(50),
    "empNum" INT REFERENCES "employee"("empNum"),
    "numSrvcRd" INT,
    "numChkPrntd" INT,
    "curUTC" TIMESTAMP REFERENCES "ErpMetadata"("curUTC")
);

CREATE TABLE IF NOT EXISTS "tax" (
    "taxId" SERIAL PRIMARY KEY,
    "guestCheckId" BIGINT REFERENCES "guestChecks"("guestCheckId"),
    "taxNum" INT,
    "txblSlsTtl" NUMERIC(10,2),
    "taxCollTtl" NUMERIC(10,2),
    "taxRate" NUMERIC(5,2),
    "type" INT
);

CREATE TABLE IF NOT EXISTS "detailLine" (
    "guestCheckLineItemId" BIGINT PRIMARY KEY,
    "guestCheckId" BIGINT REFERENCES "guestChecks"("guestCheckId"),
    "rvcNum" INT,
    "dtlOtNum" INT,
    "dtlOcNum" INT,
    "lineNum" INT,
    "dtlId" INT,
    "detailUTC" TIMESTAMP,
    "detailLcl" TIMESTAMP,
    "lastUpdateUTC" TIMESTAMP,
    "lastUpdateLcl" TIMESTAMP,
    "busDt" DATE,
    "wsNum" INT,
    "dspTtl" NUMERIC(10,2),
    "dspQty" INT,
    "aggTtl" NUMERIC(10,2),
    "aggQty" INT,
    "chkEmpId" BIGINT,
    "chkEmpNum" INT,
    "svcRndNum" INT,
    "seatNum" INT
);

CREATE TABLE IF NOT EXISTS "menuItem" (
    "menuItemId" SERIAL PRIMARY KEY,
    "guestCheckLineItemId" BIGINT REFERENCES "detailLine"("guestCheckLineItemId"),
    "miNum" INT,
    "modFlag" BOOLEAN,
    "inclTax" NUMERIC(12,6),
    "activeTaxes" VARCHAR(50),
    "prcLvl" INT
);

CREATE TABLE IF NOT EXISTS "discount" (
    "discountId" SERIAL PRIMARY KEY,
    "guestCheckLineItemId" BIGINT REFERENCES "detailLine"("guestCheckLineItemId"),
    "discountType" VARCHAR(255),
    "discountValue" NUMERIC(10,2),
    "isPercent" BOOLEAN
);

CREATE TABLE IF NOT EXISTS "serviceCharge" (
    "serviceChargeId" SERIAL PRIMARY KEY,
    "guestCheckLineItemId" BIGINT REFERENCES "detailLine"("guestCheckLineItemId"),
    "chargeName" VARCHAR(255),
    "chargeValue" NUMERIC(10,2)
);

CREATE TABLE IF NOT EXISTS "tenderMedia" (
    "tenderMediaId" SERIAL PRIMARY KEY,
    "guestCheckLineItemId" BIGINT REFERENCES "detailLine"("guestCheckLineItemId"),
    "mediaType" VARCHAR(100),
    "amount" NUMERIC(10,2)
);

CREATE TABLE IF NOT EXISTS "errorCode" (
    "errorCodeId" SERIAL PRIMARY KEY,
    "guestCheckLineItemId" BIGINT REFERENCES "detailLine"("guestCheckLineItemId"),
    "code" VARCHAR(50),
    "message" VARCHAR(255)
);