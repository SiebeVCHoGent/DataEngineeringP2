-- Database creation file

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

--
-- TOC entry 3 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

DO $$
BEGIN

    IF NOT EXISTS(
        SELECT schema_name
          FROM information_schema.schemata
          WHERE schema_name = 'public'
      )
    THEN
      EXECUTE 'CREATE SCHEMA public';
    END IF;

END
$$;


ALTER SCHEMA public OWNER TO postgres;

--
-- TOC entry 3377 (class 0 OID 0)
-- Dependencies: 3
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 221 (class 1259 OID 24765)
-- Name: codingtreeitem; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.codingtreeitem (
    id bigint NOT NULL,
    searchterm bigint NOT NULL,
    verslag bigint NOT NULL,
    score bigint
);


ALTER TABLE public.codingtreeitem OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 24764)
-- Name: codingtreeitem_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.codingtreeitem ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.codingtreeitem_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 211 (class 1259 OID 24628)
-- Name: gemeente; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gemeente (
    postcode text NOT NULL,
    naam text NOT NULL
);


ALTER TABLE public.gemeente OWNER TO postgres;

--
-- TOC entry 209 (class 1259 OID 24609)
-- Name: hoofdsector; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.hoofdsector (
    id smallint NOT NULL,
    naam text NOT NULL
);


ALTER TABLE public.hoofdsector OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 24752)
-- Name: jaarverslag; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jaarverslag (
    id text NOT NULL,
    verslag bigint NOT NULL,
    url text NOT NULL,
    tekst text
);


ALTER TABLE public.jaarverslag OWNER TO postgres;

--
-- TOC entry 212 (class 1259 OID 24635)
-- Name: kmo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.kmo (
    ondernemingsnummer text NOT NULL,
    naam text NOT NULL,
    email text,
    telefoonnummer text,
    adres text,
    beursgenoteerd boolean NOT NULL,
    "isB2B" boolean NOT NULL,
    postcode text NOT NULL,
    sector integer NOT NULL
);


ALTER TABLE public.kmo OWNER TO postgres;

--
-- TOC entry 213 (class 1259 OID 24678)
-- Name: searchterm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.searchterm (
    id bigint NOT NULL,
    term text NOT NULL,
    parent bigint
);


ALTER TABLE public.searchterm OWNER TO postgres;

--
-- TOC entry 210 (class 1259 OID 24616)
-- Name: sector; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sector (
    id integer NOT NULL,
    naam text NOT NULL,
    hoofdsector smallint
);


ALTER TABLE public.sector OWNER TO postgres;

--
-- TOC entry 214 (class 1259 OID 24716)
-- Name: sector_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.sector ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.sector_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 215 (class 1259 OID 24726)
-- Name: verslag; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.verslag (
    id bigint NOT NULL,
    jaar bigint NOT NULL,
    ondernemingsnummer text NOT NULL,
    aantalwerkenemers integer,
    omzet bigint,
    balanstotaal bigint
);


ALTER TABLE public.verslag OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 24751)
-- Name: verslag_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.verslag ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.verslag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 217 (class 1259 OID 24739)
-- Name: website; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.website (
    id bigint NOT NULL,
    verslag bigint NOT NULL,
    url text NOT NULL,
    tekst text
);


ALTER TABLE public.website OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 24738)
-- Name: website_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.website ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.website_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 222 (class 1259 OID 24874)
-- Name: woord; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.woord (
    id bigint NOT NULL,
    woord text NOT NULL,
    searchterm bigint NOT NULL
);


ALTER TABLE public.woord OWNER TO postgres;

--
-- TOC entry 3220 (class 2606 OID 24769)
-- Name: codingtreeitem codingtreeitem_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.codingtreeitem
    ADD CONSTRAINT codingtreeitem_pkey PRIMARY KEY (id);


--
-- TOC entry 3208 (class 2606 OID 24634)
-- Name: gemeente gemeente_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gemeente
    ADD CONSTRAINT gemeente_pkey PRIMARY KEY (postcode);


--
-- TOC entry 3204 (class 2606 OID 24615)
-- Name: hoofdsector hoofdsector_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hoofdsector
    ADD CONSTRAINT hoofdsector_pkey PRIMARY KEY (id);


--
-- TOC entry 3218 (class 2606 OID 24758)
-- Name: jaarverslag jaarverslag_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jaarverslag
    ADD CONSTRAINT jaarverslag_pkey PRIMARY KEY (id);


--
-- TOC entry 3210 (class 2606 OID 24641)
-- Name: kmo kmo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kmo
    ADD CONSTRAINT kmo_pkey PRIMARY KEY (ondernemingsnummer);


--
-- TOC entry 3212 (class 2606 OID 24684)
-- Name: searchterm searchterm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.searchterm
    ADD CONSTRAINT searchterm_pkey PRIMARY KEY (id);


--
-- TOC entry 3206 (class 2606 OID 24622)
-- Name: sector sector_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sector
    ADD CONSTRAINT sector_pkey PRIMARY KEY (id);


--
-- TOC entry 3214 (class 2606 OID 24732)
-- Name: verslag verslag_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.verslag
    ADD CONSTRAINT verslag_pkey PRIMARY KEY (id);


--
-- TOC entry 3216 (class 2606 OID 24745)
-- Name: website website_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.website
    ADD CONSTRAINT website_pkey PRIMARY KEY (id);


--
-- TOC entry 3222 (class 2606 OID 24880)
-- Name: woord woord_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.woord
    ADD CONSTRAINT woord_pkey PRIMARY KEY (id);


--
-- TOC entry 3223 (class 2606 OID 24623)
-- Name: sector hoofdsector; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sector
    ADD CONSTRAINT hoofdsector FOREIGN KEY (hoofdsector) REFERENCES public.hoofdsector(id) NOT VALID;


--
-- TOC entry 3227 (class 2606 OID 24733)
-- Name: verslag ondernemingsnummer_x; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.verslag
    ADD CONSTRAINT ondernemingsnummer_x FOREIGN KEY (ondernemingsnummer) REFERENCES public.kmo(ondernemingsnummer);


--
-- TOC entry 3226 (class 2606 OID 24685)
-- Name: searchterm parentx; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.searchterm
    ADD CONSTRAINT parentx FOREIGN KEY (parent) REFERENCES public.searchterm(id) NOT VALID;


--
-- TOC entry 3224 (class 2606 OID 24642)
-- Name: kmo postcodex; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kmo
    ADD CONSTRAINT postcodex FOREIGN KEY (postcode) REFERENCES public.gemeente(postcode);


--
-- TOC entry 3231 (class 2606 OID 24775)
-- Name: codingtreeitem searchterm_x; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.codingtreeitem
    ADD CONSTRAINT searchterm_x FOREIGN KEY (searchterm) REFERENCES public.searchterm(id);


--
-- TOC entry 3232 (class 2606 OID 24881)
-- Name: woord searchterm_x; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.woord
    ADD CONSTRAINT searchterm_x FOREIGN KEY (searchterm) REFERENCES public.searchterm(id) NOT VALID;


--
-- TOC entry 3225 (class 2606 OID 24647)
-- Name: kmo sectorx; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kmo
    ADD CONSTRAINT sectorx FOREIGN KEY (sector) REFERENCES public.sector(id);


--
-- TOC entry 3228 (class 2606 OID 24746)
-- Name: website verslag_x; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.website
    ADD CONSTRAINT verslag_x FOREIGN KEY (verslag) REFERENCES public.verslag(id);


--
-- TOC entry 3230 (class 2606 OID 24770)
-- Name: codingtreeitem verslag_x; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.codingtreeitem
    ADD CONSTRAINT verslag_x FOREIGN KEY (verslag) REFERENCES public.verslag(id);


--
-- TOC entry 3229 (class 2606 OID 24759)
-- Name: jaarverslag vesrlag_x; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jaarverslag
    ADD CONSTRAINT vesrlag_x FOREIGN KEY (verslag) REFERENCES public.verslag(id);


-- Completed on 2022-10-10 13:56:20

--
-- PostgreSQL database dump complete
--

