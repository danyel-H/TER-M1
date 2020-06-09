function modif_infos()
{
    document.getElementById("nom").disabled = false;
    document.getElementById("desc").disabled = false;
    document.getElementById("lieu").disabled = false;
    document.getElementById("dateDebut").disabled = false;
    document.getElementById("heureDebut").disabled = false;
    document.getElementById("dateFin").disabled = false;
    document.getElementById("heureFin").disabled = false;

    document.getElementById("bouton").hidden = true;
    document.getElementById("btn_modif").hidden = false;
}