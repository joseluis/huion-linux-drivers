#![allow(dead_code)]
#![allow(unused_imports)]
#![allow(unused_variables)]


use std::fs;

use evdev_rs::*;
use evdev_rs::enums::*;
use globset::Glob;

const HUION_VENDOR_ID:  u16 = 0x256c; // 9580
const HUION_PRODUCT_ID: u16 = 0x006e; // 110

mod tablet; use tablet::*;
mod settings; use settings::*;
//mod config;
//mod args;
//mod gui;


fn main() {
    let mut settings = Settings::new();

    find_tablet(&mut settings);
}


/// Tries to find the tablet searching through the input devices
fn find_tablet(settings: &mut Settings) {
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

    // TEMP DEBUG
    println!("\n---\n   {:?}", settings)
}
