use std::collections::HashMap;
use std::fs;
use std::io;

use evdev_rs::*;
use evdev_rs::enums::*;
use evdev_rs::enums::EV_KEY::KEY_RESERVED;
use std::hash::Hash;
use globset::Glob;

use crate::settings::Settings;

const HUION_VENDOR_ID:  u16 = 0x256c; // 9580
const HUION_PRODUCT_ID: u16 = 0x006e; // 110

/// Represents a Huion Tablet
#[derive(Debug)]
pub struct Tablet {
    name: String,
    location: String,
    identifier: String,
    version: u16,
    properties: Vec<InputProp>,
    events: Vec<EventCode>,
    // abs_info: HashMap<EventCode, AbsInfo>
    abs_info: HashMap<String, AbsInfo>
}

#[derive(Debug)]
pub struct AbsInfo {
    value: i32,
    min: i32,
    max: i32,
    fuzz: i32,
    flat: i32,
    resolution: i32
}



impl Tablet {
    /// Tries to find all connected Huion tablets and adds them to the settings
    pub fn find_tablets(settings: &mut Settings) {
        let glob = Glob::new("/dev/input/event*").unwrap().compile_matcher();
        let paths = fs::read_dir("/dev/input/").expect("Couldn't read /dev/input/");

        for entry in paths {
            if let Ok(entry) = entry {

                if glob.is_match(entry.path().as_path()) {

                    sudo::escalate_if_needed().expect("sudo failed");
                    let f = std::fs::File::open(entry.path().as_path()).unwrap();

                    let mut d = Device::new().unwrap();
                    d.set_fd(f).unwrap();

                    if d.vendor_id() == HUION_VENDOR_ID && d.product_id() == HUION_PRODUCT_ID {
                        settings.add(Tablet::new(&d));
                    }
                }
            }
        }
    }

    /// Creates a new Tablet from an input Device
    // TODO: store the device, or clone it !
    pub fn new(dev: &Device) -> Tablet {
        let mut tablet = Tablet {
            name: String::new(),
            location: String::new(),
            identifier: String::new(),
            version: 0,
            properties: Vec::new(),
            events: Vec::new(),
            abs_info: HashMap::new(),
        };

        tablet.name = dev.name().unwrap_or("").to_string();
        tablet.location = dev.phys().unwrap_or("").to_string();
        tablet.location = dev.phys().unwrap_or("").to_string();
        tablet.identifier = dev.uniq().unwrap_or("").to_string();
        tablet.version = dev.version();

        tablet.fill_properties(dev);
        tablet.fill_events(dev);
        tablet
    }

    /// Fill the tablet available properties from a Device
    pub fn fill_properties(&mut self, dev:&Device) {
        for input_prop in InputProp::INPUT_PROP_POINTER.iter() {
            if dev.has(&input_prop) {
                self.properties.push(input_prop);
            }
        }
    }

    /// Fill the tablet available events from a Device
    pub fn fill_events(&mut self, dev:&Device) {
        for ev_type in EventType::EV_SYN.iter() {
            match ev_type {
                EventType::EV_KEY => self.fill_events_code_bits(dev,
                                                   &EventCode::EV_KEY(EV_KEY::KEY_RESERVED),
                                                   &EventCode::EV_KEY(EV_KEY::KEY_MAX)),
                EventType::EV_REL => self.fill_events_code_bits(dev,
                                                 &EventCode::EV_REL(EV_REL::REL_X),
                                                 &EventCode::EV_REL(EV_REL::REL_MAX)),
                EventType::EV_ABS => self.fill_events_code_bits(dev,
                                                 &EventCode::EV_ABS(EV_ABS::ABS_X),
                                                  &EventCode::EV_ABS(EV_ABS::ABS_MAX)),
                _ => (),
            }
        }
    }

    fn fill_events_code_bits(&mut self, dev: &Device, ev_code: &EventCode, max: &EventCode) {
        for code in ev_code.iter() {
            if code == *max { break; }
            if !dev.has(&code) {  continue; }

            self.events.push(code.clone());

            if let EventCode::EV_ABS(k) = code {

                let code = EventCode::EV_ABS(k.clone());
                let abs = dev.abs_info(&code).unwrap();

                self.abs_info.insert(code.to_string(),AbsInfo {
                    value: abs.value,
                    min: abs.minimum,
                    max: abs.maximum,
                    fuzz: abs.fuzz,
                    flat: abs.flat,
                    resolution: abs.resolution
                });
            }
        }
    }
}
