ALTER TABLE cykelstativ ADD SPATIAL INDEX(wkb_geometry);
ALTER TABLE f_udsatte_byomraader ADD SPATIAL INDEX(wkb_geometry);
ALTER TABLE parkregister ADD SPATIAL INDEX(wkb_geometry);
ALTER TABLE tungvognsnet ADD SPATIAL INDEX(wkb_geometry);
ALTER TABLE gadetraer ADD SPATIAL INDEX(wkb_geometry);