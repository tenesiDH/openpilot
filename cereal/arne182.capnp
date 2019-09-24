using Cxx = import "./include/c++.capnp";
$Cxx.namespace("cereal");

using Java = import "./include/java.capnp";
$Java.package("ai.comma.openpilot.cereal");
$Java.outerClassname("arne182");

@0xca61a35dedbd6328;

struct Arne182Status { 
  blindspot @0 :Bool;
  distanceToggle @1 :Float32;
  laneDepartureToggle @2 :Bool;
  accSlowToggle @3 :Bool;
  blindspotside @4 :Float32;
  readdistancelines @5 :Float32;
  gasbuttonstatus @6 :Float32;
  lkMode @7 :Bool;
  }
