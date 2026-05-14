import streamlit as st


class WorkspaceState:

    # -----------------------------------
    # CASE SELECTION
    # -----------------------------------
    @staticmethod
    def get_selected_case_id():

        return st.session_state.get(
            "selected_case_id"
        )

    @staticmethod
    def set_selected_case_id(case_id):

        st.session_state[
            "selected_case_id"
        ] = case_id

    # -----------------------------------
    # EVIDENCE SELECTION
    # -----------------------------------
    @staticmethod
    def get_selected_evidence_id():

        return st.session_state.get(
            "selected_evidence_id"
        )

    @staticmethod
    def set_selected_evidence_id(evidence_id):

        st.session_state[
            "selected_evidence_id"
        ] = evidence_id

    # -----------------------------------
    # ENTITY SELECTION
    # -----------------------------------
    @staticmethod
    def get_selected_entity():

        return st.session_state.get(
            "selected_entity"
        )

    @staticmethod
    def set_selected_entity(entity):

        st.session_state[
            "selected_entity"
        ] = entity

    # -----------------------------------
    # TIMELINE FILTERS
    # -----------------------------------
    @staticmethod
    def get_timeline_filters():

        return st.session_state.get(
            "timeline_filters",
            {}
        )

    @staticmethod
    def set_timeline_filters(filters):

        st.session_state[
            "timeline_filters"
        ] = filters

    # -----------------------------------
    # EVIDENCE FILTERS
    # -----------------------------------
    @staticmethod
    def get_evidence_filters():

        return st.session_state.get(
            "evidence_filters",
            {}
        )

    @staticmethod
    def set_evidence_filters(filters):

        st.session_state[
            "evidence_filters"
        ] = filters

    # -----------------------------------
    # WORKSPACE RESET
    # -----------------------------------
    @staticmethod
    def clear_workspace():

        keys = [
            "selected_case_id",
            "selected_evidence_id",
            "selected_entity",
            "timeline_filters",
            "evidence_filters",
        ]

        for key in keys:

            if key in st.session_state:

                del st.session_state[key]