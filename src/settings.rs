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

    /// Adds a tablet to the settings
    pub fn add(&mut self, tablet: Tablet) {
        // println!("\n---\n   {:#?}", &tablet); // DEBUG: print tablet
        self.tablets.push(tablet);
    }

    /// Returns the number of tablets in settings
    pub fn num_tablets(&self) -> usize { self.tablets.len() }

    /// Returns a reference to the current tablet
    pub fn current_tablet(&self) -> &Tablet { &self.tablets[self.current_tablet] }

    /// Returns a mutable reference to the current tablet
    pub fn current_tablet_mut(&mut self) -> &mut Tablet { &mut self.tablets[self.current_tablet] }
}

