-- STATUS: CANDIDATE (template; tag and archive names not yet known)
-- Source: WinCC OLE DB provider Tag Logging syntax.
-- Reads the last 10 minutes of one archived tag. Replace <ArchiveName> and
-- <TagName> with names verified from chengxing.mdf.
-- Note: the archive copy has no Tag Logging data (only AlarmLogging), so
-- this query can only be tested against the live system.
TAG:R,'<ArchiveName>\<TagName>','0000-00-00 00:10:00.000','0000-00-00 00:00:00.000'
