"""
PNML Parser - Task 1

Parses Petri nets from PNML (Petri Net Markup Language) files.
Supports the standard PNML format used for Petri net interchange.

PNML Structure:
<pnml>
  <net>
    <place id="p1">
      <initialMarking><text>1</text></initialMarking>
    </place>
    <transition id="t1"/>
    <arc source="p1" target="t1"/>
  </net>
</pnml>
"""

from lxml import etree
from petri_net import PetriNet, Place, Transition, Arc
from typing import Optional


class PNMLParser:
    """Parser for PNML files."""
    
    # Common PNML namespaces
    NAMESPACES = {
        'pnml': 'http://www.pnml.org/version-2009/grammar/pnml',
        'pnml2': 'http://www.pnml.org/version-2003/grammar/pnml'
    }
    
    @staticmethod
    def parse_file(filepath: str) -> PetriNet:
        """
        Parse a PNML file and return a PetriNet object.
        
        Args:
            filepath: Path to the PNML file
            
        Returns:
            PetriNet object
            
        Raises:
            ValueError: If the file is invalid or inconsistent
        """
        try:
            tree = etree.parse(filepath)
            root = tree.getroot()
        except Exception as e:
            raise ValueError(f"Failed to parse XML file: {e}")
        
        petri_net = PetriNet()
        
        # Try to find net element with or without namespace
        net = PNMLParser._find_element(root, 'net')
        if net is None:
            raise ValueError("No <net> element found in PNML file")
        
        # Parse places
        for place_elem in PNMLParser._find_all_elements(net, 'place'):
            place = PNMLParser._parse_place(place_elem)
            petri_net.add_place(place)
        
        # Parse transitions
        for trans_elem in PNMLParser._find_all_elements(net, 'transition'):
            transition = PNMLParser._parse_transition(trans_elem)
            petri_net.add_transition(transition)
        
        # Parse arcs
        for arc_elem in PNMLParser._find_all_elements(net, 'arc'):
            arc = PNMLParser._parse_arc(arc_elem)
            petri_net.add_arc(arc)
        
        # Build indices for efficient operations
        petri_net.build_indices()
        
        # Validate consistency
        PNMLParser._validate_petri_net(petri_net)
        
        return petri_net
    
    @staticmethod
    def _find_element(parent, tag: str):
        """Find element with or without namespace."""
        # Try without namespace
        elem = parent.find(tag)
        if elem is not None:
            return elem
        
        # Try with namespaces
        for ns_prefix, ns_uri in PNMLParser.NAMESPACES.items():
            elem = parent.find(f'{{{ns_uri}}}{tag}')
            if elem is not None:
                return elem
        
        return None
    
    @staticmethod
    def _find_all_elements(parent, tag: str):
        """Find all elements with or without namespace."""
        # Try without namespace
        elems = parent.findall(tag)
        if elems:
            return elems
        
        # Try with namespaces
        for ns_prefix, ns_uri in PNMLParser.NAMESPACES.items():
            elems = parent.findall(f'{{{ns_uri}}}{tag}')
            if elems:
                return elems
        
        return []
    
    @staticmethod
    def _parse_place(place_elem) -> Place:
        """Parse a place element."""
        place_id = place_elem.get('id')
        if not place_id:
            raise ValueError("Place element missing 'id' attribute")
        
        # Parse name (optional)
        name = ""
        name_elem = PNMLParser._find_element(place_elem, 'name')
        if name_elem is not None:
            text_elem = PNMLParser._find_element(name_elem, 'text')
            if text_elem is not None and text_elem.text:
                name = text_elem.text.strip()
        
        # Parse initial marking (optional)
        initial_tokens = 0
        marking_elem = PNMLParser._find_element(place_elem, 'initialMarking')
        if marking_elem is not None:
            text_elem = PNMLParser._find_element(marking_elem, 'text')
            if text_elem is not None and text_elem.text:
                try:
                    initial_tokens = int(text_elem.text.strip())
                except ValueError:
                    raise ValueError(f"Invalid initial marking for place {place_id}")
        
        return Place(id=place_id, name=name or place_id, initial_tokens=initial_tokens)
    
    @staticmethod
    def _parse_transition(trans_elem) -> Transition:
        """Parse a transition element."""
        trans_id = trans_elem.get('id')
        if not trans_id:
            raise ValueError("Transition element missing 'id' attribute")
        
        # Parse name (optional)
        name = ""
        name_elem = PNMLParser._find_element(trans_elem, 'name')
        if name_elem is not None:
            text_elem = PNMLParser._find_element(name_elem, 'text')
            if text_elem is not None and text_elem.text:
                name = text_elem.text.strip()
        
        return Transition(id=trans_id, name=name or trans_id)
    
    @staticmethod
    def _parse_arc(arc_elem) -> Arc:
        """Parse an arc element."""
        source = arc_elem.get('source')
        target = arc_elem.get('target')
        
        if not source or not target:
            raise ValueError("Arc element missing 'source' or 'target' attribute")
        
        # Parse weight (optional, default is 1)
        weight = 1
        inscription_elem = PNMLParser._find_element(arc_elem, 'inscription')
        if inscription_elem is not None:
            text_elem = PNMLParser._find_element(inscription_elem, 'text')
            if text_elem is not None and text_elem.text:
                try:
                    weight = int(text_elem.text.strip())
                except ValueError:
                    raise ValueError(f"Invalid arc weight: {text_elem.text}")
        
        return Arc(source=source, target=target, weight=weight)
    
    @staticmethod
    def _validate_petri_net(petri_net: PetriNet):
        """
        Validate the consistency of the parsed Petri net.
        Checks for missing nodes referenced in arcs.
        """
        place_ids = set(petri_net.places.keys())
        transition_ids = set(petri_net.transitions.keys())
        all_node_ids = place_ids | transition_ids
        
        for arc in petri_net.arcs:
            if arc.source not in all_node_ids:
                raise ValueError(f"Arc references unknown source node: {arc.source}")
            if arc.target not in all_node_ids:
                raise ValueError(f"Arc references unknown target node: {arc.target}")
            
            # Check that arcs connect places to transitions or vice versa
            source_is_place = arc.source in place_ids
            target_is_place = arc.target in place_ids
            
            if source_is_place == target_is_place:
                raise ValueError(
                    f"Invalid arc: {arc.source} -> {arc.target}. "
                    "Arcs must connect places to transitions or transitions to places."
                )


def load_petri_net(filepath: str) -> PetriNet:
    """
    Convenience function to load a Petri net from a PNML file.
    
    Args:
        filepath: Path to the PNML file
        
    Returns:
        PetriNet object
    """
    return PNMLParser.parse_file(filepath)

