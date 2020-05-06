#![allow(dead_code)]
#![allow(unused_imports)]
#![allow(unused_variables)]


mod tablet; use tablet::Tablet;
mod settings; use settings::Settings;
//mod config;
//mod args;
//mod gui;


fn main() {
    let mut settings = Settings::new();
    Tablet::find_tablets(&mut settings);

    //Tablet::print_events()
}
