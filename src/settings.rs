use crate::tablet::Tablet;

/// Stores global settings
#[derive(Debug)]
pub struct Settings{
    tablets: Vec<Tablet>,
    current_tablet: usize,
}
impl Settings {
    pub fn new() -> Settings {
        Settings {
            tablets: Vec::new(),
            current_tablet: 0,
        }
    }
    pub fn add(&mut self, tablet: Tablet) { self.tablets.push(tablet) }
}

