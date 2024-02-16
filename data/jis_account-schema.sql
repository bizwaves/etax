--
-- PostgreSQL database dump
--

-- Dumped from database version 16.0
-- Dumped by pg_dump version 16.0

-- Started on 2024-02-16 15:50:02

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 231 (class 1259 OID 16459)
-- Name: jis_account_a; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jis_account_a (
    id integer NOT NULL,
    code integer NOT NULL,
    name character varying(256) NOT NULL
);


ALTER TABLE public.jis_account_a OWNER TO postgres;

--
-- TOC entry 4920 (class 0 OID 0)
-- Dependencies: 231
-- Name: TABLE jis_account_a; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.jis_account_a IS 'JISX0406-1984 大分類コード';


--
-- TOC entry 4921 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN jis_account_a.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_a.id IS 'コード（形式：１桁）';


--
-- TOC entry 4922 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN jis_account_a.code; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_a.code IS 'コード（形式：４桁）';


--
-- TOC entry 4923 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN jis_account_a.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_a.name IS '勘定科目名';


--
-- TOC entry 232 (class 1259 OID 16462)
-- Name: jis_account_b; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jis_account_b (
    jisacc_a_id integer NOT NULL,
    id integer NOT NULL,
    code integer NOT NULL,
    name character varying(256) NOT NULL,
    should_be_deducted boolean DEFAULT false NOT NULL
);


ALTER TABLE public.jis_account_b OWNER TO postgres;

--
-- TOC entry 4924 (class 0 OID 0)
-- Dependencies: 232
-- Name: TABLE jis_account_b; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.jis_account_b IS 'JISX0406-1984 中分類コード';


--
-- TOC entry 4925 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN jis_account_b.jisacc_a_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_b.jisacc_a_id IS '親 JISX0406-1984 大分類コード';


--
-- TOC entry 4926 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN jis_account_b.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_b.id IS 'コード（形式：１桁）';


--
-- TOC entry 4927 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN jis_account_b.code; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_b.code IS 'コード（形式：４桁）';


--
-- TOC entry 4928 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN jis_account_b.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_b.name IS '勘定科目名';


--
-- TOC entry 4929 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN jis_account_b.should_be_deducted; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_b.should_be_deducted IS '控除すべき勘定科目';


--
-- TOC entry 233 (class 1259 OID 16466)
-- Name: jis_account_c; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jis_account_c (
    jisacc_b_id integer NOT NULL,
    id integer NOT NULL,
    code integer NOT NULL,
    name character varying(256) NOT NULL,
    should_be_deducted boolean DEFAULT false NOT NULL
);


ALTER TABLE public.jis_account_c OWNER TO postgres;

--
-- TOC entry 4930 (class 0 OID 0)
-- Dependencies: 233
-- Name: TABLE jis_account_c; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.jis_account_c IS 'JISX0406-1984 小分類コード';


--
-- TOC entry 4931 (class 0 OID 0)
-- Dependencies: 233
-- Name: COLUMN jis_account_c.jisacc_b_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_c.jisacc_b_id IS '親 JISX0406-1984 中分類コード';


--
-- TOC entry 4932 (class 0 OID 0)
-- Dependencies: 233
-- Name: COLUMN jis_account_c.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_c.id IS 'コード（形式：３桁）';


--
-- TOC entry 4933 (class 0 OID 0)
-- Dependencies: 233
-- Name: COLUMN jis_account_c.code; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_c.code IS 'コード（形式：４桁）';


--
-- TOC entry 4934 (class 0 OID 0)
-- Dependencies: 233
-- Name: COLUMN jis_account_c.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_c.name IS '勘定科目名';


--
-- TOC entry 4935 (class 0 OID 0)
-- Dependencies: 233
-- Name: COLUMN jis_account_c.should_be_deducted; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_c.should_be_deducted IS '控除すべき勘定科目';


--
-- TOC entry 234 (class 1259 OID 16470)
-- Name: jis_account_d; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jis_account_d (
    jisacc_c_id integer NOT NULL,
    id integer NOT NULL,
    code integer NOT NULL,
    name character varying(256) NOT NULL,
    should_be_deducted boolean DEFAULT false NOT NULL,
    level text
);


ALTER TABLE public.jis_account_d OWNER TO postgres;

--
-- TOC entry 4936 (class 0 OID 0)
-- Dependencies: 234
-- Name: TABLE jis_account_d; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.jis_account_d IS 'JISX0406-1984 細分類コード';


--
-- TOC entry 4937 (class 0 OID 0)
-- Dependencies: 234
-- Name: COLUMN jis_account_d.jisacc_c_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_d.jisacc_c_id IS '親 JISX0406-1984 小分類コード';


--
-- TOC entry 4938 (class 0 OID 0)
-- Dependencies: 234
-- Name: COLUMN jis_account_d.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_d.id IS 'コード（形式：４桁）';


--
-- TOC entry 4939 (class 0 OID 0)
-- Dependencies: 234
-- Name: COLUMN jis_account_d.code; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_d.code IS 'コード（形式：４桁）';


--
-- TOC entry 4940 (class 0 OID 0)
-- Dependencies: 234
-- Name: COLUMN jis_account_d.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_d.name IS '勘定科目名';


--
-- TOC entry 4941 (class 0 OID 0)
-- Dependencies: 234
-- Name: COLUMN jis_account_d.should_be_deducted; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.jis_account_d.should_be_deducted IS '控除すべき勘定科目';


--
-- TOC entry 4762 (class 2606 OID 16498)
-- Name: jis_account_a jis_account_a_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jis_account_a
    ADD CONSTRAINT jis_account_a_pkey PRIMARY KEY (id);


--
-- TOC entry 4764 (class 2606 OID 16500)
-- Name: jis_account_b jis_account_b_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jis_account_b
    ADD CONSTRAINT jis_account_b_pkey PRIMARY KEY (id);


--
-- TOC entry 4766 (class 2606 OID 16502)
-- Name: jis_account_c jis_account_c_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jis_account_c
    ADD CONSTRAINT jis_account_c_pkey PRIMARY KEY (id);


--
-- TOC entry 4768 (class 2606 OID 16504)
-- Name: jis_account_d jis_account_d_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jis_account_d
    ADD CONSTRAINT jis_account_d_pkey PRIMARY KEY (id);


--
-- TOC entry 4769 (class 2606 OID 16518)
-- Name: jis_account_b jis_account_b_jisacc_a_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jis_account_b
    ADD CONSTRAINT jis_account_b_jisacc_a_id_fkey FOREIGN KEY (jisacc_a_id) REFERENCES public.jis_account_a(id);


--
-- TOC entry 4770 (class 2606 OID 16523)
-- Name: jis_account_c jis_account_c_jisacc_b_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jis_account_c
    ADD CONSTRAINT jis_account_c_jisacc_b_id_fkey FOREIGN KEY (jisacc_b_id) REFERENCES public.jis_account_b(id);


--
-- TOC entry 4771 (class 2606 OID 16528)
-- Name: jis_account_d jis_account_d_jisacc_c_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jis_account_d
    ADD CONSTRAINT jis_account_d_jisacc_c_id_fkey FOREIGN KEY (jisacc_c_id) REFERENCES public.jis_account_c(id);


-- Completed on 2024-02-16 15:50:07

--
-- PostgreSQL database dump complete
--

